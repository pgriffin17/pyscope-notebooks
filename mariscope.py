import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    from pyscope.observatory import Observatory
    from pyscope.telrun import mk_mosaic_schedule, schedtel
    from astropy import coordinates as coord
    import logging
    import time
    import numpy as np
    import pathlib

    logging.basicConfig(level=logging.INFO)
    return (
        Observatory,
        coord,
        logging,
        mk_mosaic_schedule,
        mo,
        np,
        pathlib,
        schedtel,
        time,
    )


@app.cell(hide_code=True)
def __(mo):
    # Create a form with multiple elements
    filters_list = ["ha", "oiii", "sii"]
    form = (
        mo.md('''
        **Observing form.**

        {target_name}

        {exp_time} {filter} {num_images}

        
    ''')
        .batch(
            target_name=mo.ui.text(label="Target name"),
            exp_time=mo.ui.number(start=0, stop=600, label="Exposure Time"),
            filter=mo.ui.dropdown(options=filters_list, value="ha", label="Filter"),
            num_images=mo.ui.number(start=1, stop=100, step=1, label="No. Images")
        )
        .form(show_clear_button=True, bordered=False)
    )
    form
    return filters_list, form


@app.cell(hide_code=True)
def __(coord, form):

    src = coord.SkyCoord.from_name(form.value["target_name"])
    print(f"Target name: {form.value["target_name"]}")
    print(f"RA: {src.ra.hms},\nDec: {src.dec.dms}")
    print(f"Exposure time: {form.value["exp_time"]} seconds")
    print(f"Filter: {form.value["filter"]}")
    print(f"Number of Images: {form.value["num_images"]}")
    return src,


@app.cell
def __(NGC2174_table, rlmt):
    mosaic_panel = 3
    object_name = f"NGC2174_{mosaic_panel}"
    src = NGC2174_table['SkyCoord'][mosaic_panel]
    # object_name = "SS4TYC 5134-1820-1" # Change name here
    # src = coord.SkyCoord("19h21m09.2835s -03d44m26.2962s", frame='icrs')
    # src = coord.SkyCoord.from_name(object_name)
    print(f"RA: {src.ra.hms},\nDec: {src.dec.dms}")
    print(src)
    # Print alt az of source
    src_altaz = rlmt.get_object_altaz(src)
    print(f"Elevation: {src_altaz.alt.deg:.2f}, Azimuth: {src_altaz.az.deg:.2f}")
    print(f"Elevation dms: {src_altaz.alt.dms}, \nAzimuth dms: {src_altaz.az.dms}")
    if src_altaz.alt.deg < 30:
        raise Exception("Source is too low to observe.")
    return mosaic_panel, object_name, src, src_altaz


@app.cell
def __(rlmt, src, src_altaz):
    # Set to g filter
    rlmt.filter_wheel.Position = 3

    # Run recentering algorithm
    if src_altaz.alt.deg < 30:
        raise Exception("Source is too low to observe.")
    rlmt.recenter(src, 
        target_x_pixel=1024, # TODO: make default center of sensor in each axis
        target_y_pixel=1024,
        exposure=3, 
        save_images=True,
        save_path="./recenter_images/",
        readout=2,
    )
    return


@app.cell
def __(capture_grism_image, num_images, object_name, rlmt):
    filter_positions = {
        "LowRes": 0,
        "HighRes": 4,
        "g": 2,
        "r": 3,
        "ha": 10,
        "oiii": 7,
        "sii": 9,
    }

    for i in range(num_images):
        filter_name = "ha"
        rlmt.filter_wheel.Position = filter_positions[filter_name]
        exp_time = 60 # in seconds
        capture_grism_image(filter_name, object_name, exp_time=exp_time, filename_prefix="tricolor")

        filter_name = "sii"
        rlmt.filter_wheel.Position = filter_positions[filter_name]
        exp_time = 60 # in seconds
        capture_grism_image(filter_name, object_name, exp_time=exp_time, filename_prefix="tricolor")

        filter_name = "oiii"
        rlmt.filter_wheel.Position = filter_positions[filter_name]
        exp_time = 60 # in seconds
        capture_grism_image(filter_name, object_name, exp_time=exp_time, filename_prefix="tricolor")
    return exp_time, filter_name, filter_positions, i


if __name__ == "__main__":
    app.run()
