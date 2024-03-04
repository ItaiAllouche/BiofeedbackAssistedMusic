


if __name__ == "__main__":
    controller = Controller(SERVER_IP)
    wanted_sf=[65,70,75,80,85]
    controller.clc_min_hr_pt(wanted_sf=wanted_sf, n_epoch=3)