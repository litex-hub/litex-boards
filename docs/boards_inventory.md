# LiteX-Boards Inventory

Generated from target and platform modules. Refresh with:

```sh
python3 .github/scripts/generate_board_inventory.py --write
```

| Target | Platform module(s) | Toolchain(s) | Default sys clk | Common features | Target no-compile test |
| --- | --- | --- | --- | --- | --- |
| `adi_adrv2crr_fmc` | adi_adrv2crr_fmc | - | `150000000.0` | PCIe | included |
| `adi_plutosdr` | adi_plutosdr | vivado | `100000000.0` | - | included |
| `alchitry_au` | alchitry_au | vivado | `83333000.0` | SPI Flash | included |
| `alchitry_au_v2` | alchitry_au_v2 | vivado | `100000000.0` | SPI Flash | included |
| `alchitry_cu` | alchitry_cu | icestorm | `50000000.0` | - | included |
| `alchitry_mojo` | alchitry_mojo | ise | `62500000.0` | Video Terminal, Video Framebuffer, Video Colorbars | included |
| `alchitry_pt_v2` | alchitry_pt_v2 | vivado | `100000000.0` | SPI Flash | included |
| `alibaba_vu13p` | alibaba_vu13p | vivado | `125000000.0` | Ethernet, Etherbone, PCIe | included |
| `alibaba_xcku3p` | alibaba_xcku3p | vivado | `100000000.0` | Ethernet, Etherbone, PCIe | included |
| `alientek_davincipro` | alientek_davincipro | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, PCIe, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `aliexpress_xc7k420t` | aliexpress_xc7k420t | vivado | `100000000.0` | SPI Flash | included |
| `aliexpress_xc7k70t` | aliexpress_xc7k70t | vivado | `90000000.0` | Ethernet, PCIe, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `alinx_ax7010` | alinx_ax7010 | - | `100000000.0` | - | included |
| `alinx_ax7020` | alinx_ax7020 | - | `100000000.0` | - | included |
| `alinx_ax7203` | alinx_ax7203 | - | `50000000.0` | PCIe, Video Framebuffer | included |
| `alinx_axau15` | alinx_axau15 | vivado | `125000000.0` | Ethernet, Etherbone, SDCard, PCIe | included |
| `alinx_axu2cga` | alinx_axu2cga | vivado | `25000000.0` | - | included |
| `altera_agilex5e_065b_premium_devkit` | altera_agilex5e_065b_premium_devkit | quartus | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard | included |
| `analog_pocket` | analog_pocket | quartus | `50000000.0` | Video Terminal, Video Framebuffer, Video Colorbars | included |
| `antmicro_artix_dc_scm` | antmicro_artix_dc_scm | vivado | `100000000.0` | Ethernet, Etherbone, PCIe | included |
| `antmicro_datacenter_ddr4_test_board` | antmicro_datacenter_ddr4_test_board | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `antmicro_lpddr4_test_board` | antmicro_lpddr4_test_board | vivado | `50000000.0` | Ethernet, Etherbone, SDCard | included |
| `antmicro_sdi_mipi_video_converter` | antmicro_sdi_mipi_video_converter | radiant | `75000000.0` | - | included |
| `arduino_mkrvidor4000` | arduino_mkrvidor4000 | - | `48000000.0` | - | included |
| `arrow_axe5000` | arrow_axe5000 | quartus | `100000000.0` | Ethernet, Etherbone | included |
| `avnet_aesku40` | avnet_aesku40 | - | `125000000.0` | Ethernet, Etherbone | included |
| `berkeleylab_marble` | berkeleylab_marble | vivado | `125000000.0` | Ethernet, Etherbone | included |
| `berkeleylab_obsidian` | berkeleylab_obsidian | vivado | `125000000.0` | Ethernet, Etherbone | included |
| `bochenjingxin_kintex7_basec` | bochenjingxin_kintex7_basec | vivado | `125000000.0` | - | included |
| `brisbaneSilicon_brs_100_gw1nr9` | brisbaneSilicon_brs_100_gw1nr9 | gowin | `27000000.0` | - | included |
| `camlink_4k` | camlink_4k | trellis | `81000000.0` | - | included |
| `colognechip_gatemate_evb` | colognechip_gatemate_evb | colognechip | `24000000.0` | SDCard, SPI SDCard, SPI Flash | included |
| `colorlight_5a_75x` | colorlight_5a_75b, colorlight_5a_75e, colorlight_i5a_907 | trellis | `60000000.0` | Ethernet, Etherbone, SPI Flash | included |
| `colorlight_i5` | colorlight_i5 | trellis | `60000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `colorlight_i9plus` | colorlight_i9plus | vivado | `100000000.0` | Ethernet, Etherbone, SPI Flash | included |
| `decklink_intensity_pro_4k` | decklink_intensity_pro_4k | vivado | `125000000.0` | PCIe | included |
| `decklink_mini_4k` | decklink_mini_4k | vivado | `148500000.0` | PCIe, SATA, Video Terminal, Video Framebuffer | included |
| `decklink_quad_hdmi_recorder` | decklink_quad_hdmi_recorder | vivado | `200000000.0` | PCIe | included |
| `digilent_arty` | digilent_arty | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, USB | included |
| `digilent_arty_s7` | digilent_arty_s7 | vivado | `100000000.0` | SPI Flash | included |
| `digilent_arty_z7` | digilent_arty_z7 | vivado | `125000000.0` | - | included |
| `digilent_atlys` | digilent_atlys | ise | `default` | Ethernet, Etherbone | included |
| `digilent_basys3` | digilent_basys3 | vivado | `75000000.0` | SDCard, SPI SDCard, Video Terminal | included |
| `digilent_cmod_a7` | digilent_cmod_a7 | vivado | `48000000.0` | SPI Flash | included |
| `digilent_genesys2` | digilent_genesys2 | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `digilent_netfpga_sume` | digilent_netfpga_sume | vivado | `125000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard | included |
| `digilent_nexys4` | digilent_nexys4 | vivado | `75000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `digilent_nexys4ddr` | digilent_nexys4ddr | vivado | `75000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `digilent_nexys_video` | digilent_nexys_video | vivado | `100000000.0` | Ethernet, SDCard, SPI SDCard, SATA, Video Terminal, Video Framebuffer, USB | included |
| `digilent_pynq_z1` | digilent_pynq_z1 | vivado | `125000000.0` | Video Terminal | included |
| `digilent_zedboard` | digilent_arty, digilent_zedboard | vivado | `100000000.0` | - | included |
| `ebaz4205` | ebaz4205 | vivado | `100000000.0` | - | included |
| `efinix_t8f81_dev_kit` | efinix_t8f81_dev_kit | efinity | `33333000.0` | - | toolchain-gated: Require Efinity toolchain. |
| `efinix_ti375_c529_dev_kit` | efinix_ti375_c529_dev_kit | efinity | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_titanium_ti60_f225_dev_kit` | efinix_titanium_ti60_f225_dev_kit | efinity | `200000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_trion_t120_bga576_dev_kit` | efinix_trion_t120_bga576_dev_kit | efinity | `75000000.0` | Ethernet, Etherbone, SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_trion_t20_bga256_dev_kit` | efinix_trion_t20_bga256_dev_kit | efinity | `45000000.0` | SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_trion_t20_mipi_dev_kit` | efinix_trion_t20_mipi_dev_kit | efinity | `100000000.0` | SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_tz170_j484_dev_kit` | efinix_tz170_j484_dev_kit | efinity | `100000000.0` | SDCard, SPI SDCard, SPI Flash | toolchain-gated: Require Efinity toolchain. |
| `efinix_xyloni_dev_kit` | efinix_xyloni_dev_kit | efinity | `33333000.0` | - | toolchain-gated: Require Efinity toolchain. |
| `ego1` | ego1 | vivado | `100000000.0` | Video Terminal | included |
| `embedfire_rise_pro` | embedfire_rise_pro | vivado | `50000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard | included |
| `enclustra_mercury_kx2` | enclustra_mercury_kx2, enclustra_st1 | vivado | `100000000.0` | - | included |
| `enclustra_mercury_xu5` | enclustra_mercury_xu5 | vivado | `125000000.0` | - | included |
| `enclustra_mercury_xu8_pe3` | enclustra_mercury_xu8_pe3 | vivado | `125000000.0` | PCIe | included |
| `fairwaves_xtrx` | fairwaves_xtrx | vivado | `125000000.0` | PCIe | included |
| `fpc_iii` | fpc_iii | trellis | `80000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard | included |
| `fpgawars_alhambra2` | fpgawars_alhambra2 | icestorm | `12000000.0` | - | included |
| `gadgetfactory_papilio_pro` | gadgetfactory_papilio_pro | ise | `80000000.0` | Video Terminal | included |
| `gsd_butterstick` | gsd_butterstick | trellis | `75000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash | included |
| `gsd_orangecrab` | gsd_orangecrab | trellis | `48000000.0` | SPI SDCard | included |
| `hackaday_hadbadge` | hackaday_hadbadge | trellis | `48000000.0` | - | included |
| `hseda_xc7a35t` | hseda_xc7a35t | vivado | `50000000.0` | SDCard, SPI Flash | included |
| `hyvision_pcie_opt01_revf` | hyvision_pcie_opt01_revf | vivado | `100000000.0` | Ethernet, Etherbone, PCIe | included |
| `ice_v_wireless` | ice_v_wireless | icestorm | `24000000.0` | - | included |
| `icebreaker` | icebreaker | icestorm | `24000000.0` | Video Terminal | included |
| `icebreaker_bitsy` | icebreaker_bitsy | icestorm | `24000000.0` | - | included |
| `icepi_zero` | icepi_zero | trellis | `50000000.0` | SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `intergalaktik_ulx5m_gs` | intergalaktik_ulx5m_gs | colognechip | `20000000.0` | SDCard, SPI SDCard, SPI Flash | included |
| `isx_im1283` | isx_im1283 | vivado | `80000000.0` | SDCard, SPI SDCard | included |
| `jungle_electronics_fireant` | jungle_electronics_fireant | efinity | `33333000.0` | - | toolchain-gated: Require Efinity toolchain. |
| `kosagi_fomu` | kosagi_fomu_pvt | icestorm | `12000000.0` | - | included |
| `kosagi_netv2` | kosagi_netv2 | vivado | `100000000.0` | Ethernet, SDCard, SPI SDCard, PCIe | included |
| `krtkl_snickerdoodle` | krtkl_snickerdoodle | vivado | `100000000.0` | - | included |
| `lambdaconcept_ecpix5` | lambdaconcept_ecpix5 | trellis | `75000000.0` | Ethernet, Etherbone, SDCard, Video Terminal, Video Framebuffer | included |
| `lattice_certuspro_nx_evn` | lattice_certuspro_nx_evn | radiant | `75000000.0` | - | included |
| `lattice_certuspro_nx_versa` | lattice_certuspro_nx_versa | radiant | `75000000.0` | PCIe | included |
| `lattice_certuspro_nx_vvml` | lattice_certuspro_nx_vvml | radiant | `75000000.0` | - | included |
| `lattice_crosslink_nx_evn` | lattice_crosslink_nx_evn | radiant | `75000000.0` | SPI Flash | included |
| `lattice_crosslink_nx_vip` | lattice_crosslink_nx_vip | radiant | `75000000.0` | - | included |
| `lattice_ecp5_evn` | lattice_ecp5_evn | trellis | `60000000.0` | - | included |
| `lattice_ecp5_vip` | lattice_ecp5_vip | trellis | `60000000.0` | - | included |
| `lattice_ice40up5k_evn` | lattice_ice40up5k_evn | icestorm | `12000000.0` | - | included |
| `lattice_versa_ecp5` | lattice_versa_ecp5 | trellis | `75000000.0` | Ethernet, Etherbone | included |
| `lckfb_ljpi` | lckfb_ljpi | gowin | `50000000.0` | SPI Flash, Video Terminal, Video Colorbars | included |
| `limesdr_mini_v2` | limesdr_mini_v2 | trellis | `80000000.0` | - | included |
| `linsn_rv901t` | linsn_rv901t | ise | `75000000.0` | Ethernet, Etherbone | included |
| `litex_acorn_baseboard` | litex_acorn_baseboard | trellis | `75000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal | included |
| `litex_acorn_baseboard_mini` | sqrl_acorn | vivado | `125000000.0` | Ethernet, Etherbone, PCIe, SATA | included |
| `logicbone` | logicbone | trellis | `75000000.0` | Ethernet, SDCard | included |
| `machdyne_kolsch` | machdyne_kolsch | colognechip | `24000000.0` | Ethernet, Etherbone, SPI SDCard, Video Terminal | included |
| `machdyne_konfekt` | machdyne_konfekt | trellis | `40000000.0` | SDCard, SPI SDCard, USB Host | included |
| `machdyne_kopflos` | machdyne_kopflos | trellis | `40000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_krote` | machdyne_krote | icestorm | `50000000.0` | - | included |
| `machdyne_lakritz` | machdyne_lakritz | trellis | `48000000.0` | SDCard, SPI SDCard, Video Framebuffer, USB Host | included |
| `machdyne_minze` | machdyne_minze | trellis | `48000000.0` | SDCard, SPI SDCard, USB Host | included |
| `machdyne_mozart_ml1` | machdyne_mozart_ml1 | trellis | `48000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_mozart_ml2` | machdyne_mozart_ml2 | trellis | `48000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_mozart_mx1` | machdyne_mozart_mx1 | vivado | `80000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_mozart_mx2` | machdyne_mozart_mx2 | vivado | `75000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_noir` | machdyne_noir | trellis | `50000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `machdyne_schoko` | machdyne_schoko | trellis | `40000000.0` | SDCard, SPI SDCard, USB Host | included |
| `machdyne_vanille` | machdyne_vanille | trellis | `48000000.0` | SDCard, SPI SDCard, USB Host | included |
| `machdyne_vivaldi_ml1` | machdyne_vivaldi_ml1 | trellis | `48000000.0` | Ethernet, SDCard, SPI SDCard, USB Host | included |
| `micronova_mercury2` | micronova_mercury2 | vivado | `50000000.0` | - | included |
| `microphase_a7_lite` | microphase_a7_lite | vivado | `100000000.0` | Ethernet, SDCard, SPI SDCard, SPI Flash | included |
| `microsoft_catapult_v3` | microsoft_catapult_v3 | quartus | `100000000.0` | - | included |
| `mist` | mist | quartus | `50000000.0` | Video Terminal | included |
| `mlkpai_fs01_dr1v90m` | mlkpai_fs01_dr1v90m | td | `25000000.0` | - | included |
| `mnt_rkx7` | mnt_rkx7 | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, USB Host | included |
| `muselab_icesugar` | muselab_icesugar | icestorm | `24000000.0` | - | included |
| `muselab_icesugar_pro` | muselab_icesugar_pro | trellis | `50000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `myir_myc_j7a100t` | myir_myc_j7a100t | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard | included |
| `myminieye_runber` | myminieye_runber | gowin | `12000000.0` | - | included |
| `newae_cw305` | newae_cw305 | vivado | `100000000.0` | - | included |
| `numato_aller` | numato_aller | vivado | `100000000.0` | PCIe | included |
| `numato_mimas_a7` | numato_mimas_a7 | vivado | `100000000.0` | Ethernet | included |
| `numato_nereid` | numato_nereid | vivado | `100000000.0` | PCIe | included |
| `numato_tagus` | numato_tagus | vivado | `100000000.0` | PCIe | included |
| `ocp_tap_timecard` | ocp_tap_timecard | vivado | `100000000.0` | PCIe | included |
| `olimex_gatemate_a1_evb` | olimex_gatemate_a1_evb | colognechip | `24000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal | included |
| `opalkelly_xem8320` | opalkelly_xem8320 | vivado | `125000000.0` | Video Terminal, Video Framebuffer | included |
| `opensourcesdrlab_kintex7` | opensourcesdrlab_kintex7 | vivado | `100000000.0` | SPI SDCard, SPI Flash, PCIe | included |
| `pano_logic_g2` | pano_logic_g2 | ise | `50000000.0` | Ethernet, Etherbone | included |
| `puzhi_p7_starlite` | puzhi_p7_starlite | vivado | `100000000.0` | Ethernet, Etherbone | included |
| `puzhi_pz_a7xxt_kfb` | puzhi_pz_a7xxt_kfb | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, PCIe, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `qmtech_10cl006` | qmtech_10cl006 | quartus | `50000000.0` | SDCard, SPI SDCard, SPI Flash | included |
| `qmtech_5cefa2` | qmtech_5cefa2 | quartus | `105000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `qmtech_5cefa5` | qmtech_5cefa5 | quartus | `80000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `qmtech_artix7_fbg484` | qmtech_artix7_fbg484 | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `qmtech_artix7_fgg676` | qmtech_artix7_fgg676 | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `qmtech_cyclone10_starterkit` | qmtech_cyclone10_starterkit | quartus | `50000000.0` | SDCard, SPI SDCard | included |
| `qmtech_ep4ce15_starter_kit` | qmtech_ep4ce15_starter_kit | quartus | `50000000.0` | - | included |
| `qmtech_ep4cex5` | qmtech_ep4cex5 | quartus | `50000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `qmtech_ep4cgx150` | qmtech_ep4cgx150 | quartus | `90000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `qmtech_kintex7_devboard` | qmtech_kintex7_devboard | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `qmtech_wukong` | qmtech_wukong | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `qmtech_xc7a35t` | qmtech_xc7a35t | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `qmtech_xc7k325t` | qmtech_daughterboard, qmtech_xc7k325t | vivado | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `quicklogic_quickfeather` | quicklogic_quickfeather | f4pga | `default` | - | No default clock. |
| `qwertyembedded_beaglewire` | qwertyembedded_beaglewire | icestorm | `50000000.0` | - | included |
| `radiona_ulx3s` | radiona_ulx3s | trellis | `50000000.0` | SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `radiona_ulx4m_ld_v2` | radiona_ulx4m_ld_v2 | - | `75000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `radiona_ulx4m_ls_v2` | radiona_ulx4m_ls_v2 | - | `50000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Framebuffer | included |
| `rcs_arctic_tern_bmc_card` | rcs_arctic_tern_bmc_card | trellis | `60000000.0` | Ethernet, Etherbone | included |
| `redpitaya` | redpitaya | vivado | `100000000.0` | - | included |
| `rz_easyfpga` | rz_easyfpga | quartus | `50000000.0` | - | included |
| `saanlima_pipistrello` | saanlima_pipistrello | ise | `default` | - | included |
| `scarabhardware_minispartan6` | scarabhardware_minispartan6 | ise | `80000000.0` | Video Terminal, Video Framebuffer | included |
| `seeedstudio_spartan_edge_accelerator` | seeedstudio_spartan_edge_accelerator | vivado | `100000000.0` | Video Terminal | included |
| `siglent_sds1104xe` | siglent_sds1104xe | vivado | `100000000.0` | Etherbone, Video Terminal, Video Framebuffer | included |
| `signaloid_c0_microsd` | signaloid_c0_microsd | icestorm | `24000000.0` | - | included |
| `simple` | - | - | `default` | - | Generic target. |
| `sipeed_slogic16u3` | sipeed_slogic16u3 | gowin | `20732000.0` | - | included |
| `sipeed_tang_console` | sipeed_tang_console | gowin | `50000000.0` | SDCard, SPI SDCard, SPI Flash, Video Terminal | included |
| `sipeed_tang_mega_138k` | sipeed_tang_mega_138k | gowin | `50000000.0` | Ethernet, Etherbone, PCIe, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `sipeed_tang_mega_138k_pro` | sipeed_tang_mega_138k_pro | gowin | `50000000.0` | Ethernet, Etherbone, PCIe, Video Terminal | included |
| `sipeed_tang_nano` | sipeed_tang_nano | gowin | `48000000.0` | - | included |
| `sipeed_tang_nano_20k` | sipeed_tang_nano_20k | gowin | `48000000.0` | SDCard, SPI SDCard, SPI Flash, Video Terminal, Video Colorbars | included |
| `sipeed_tang_nano_4k` | sipeed_tang_nano_4k | gowin | `27000000.0` | Video Terminal | included |
| `sipeed_tang_nano_9k` | sipeed_tang_nano_9k | gowin | `27000000.0` | SPI SDCard, Video Terminal | included |
| `sipeed_tang_primer` | sipeed_tang_primer | td | `24000000.0` | - | included |
| `sipeed_tang_primer_20k` | sipeed_tang_primer_20k | gowin | `48000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, SPI Flash, Video Terminal | included |
| `sipeed_tang_primer_25k` | sipeed_tang_primer_25k | gowin | `50000000.0` | SPI Flash | included |
| `sitlinv_a_e115fb` | sitlinv_a_e115fb | quartus | `50000000.0` | - | included |
| `sitlinv_stlv7325_v1` | sitlinv_stlv7325_v1 | - | `100000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, PCIe, SATA, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `sitlinv_stlv7325_v2` | sitlinv_stlv7325_v2 | - | `100000000.0` | Ethernet, SDCard, SPI SDCard, PCIe, SATA, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `sitlinv_xc7k420t` | sitlinv_xc7k420t | - | `100000000.0` | PCIe, SATA | included |
| `sqrl_acorn` | sqrl_acorn | vivado | `100000000.0` | SPI SDCard, PCIe, SATA | included |
| `sqrl_fk33` | sqrl_fk33 | vivado | `125000000.0` | PCIe | included |
| `sqrl_xcu1525` | sqrl_xcu1525 | vivado | `125000000.0` | Ethernet, Etherbone, PCIe, SATA | included |
| `terasic_atum_a3_nano` | terasic_atum_a3_nano | quartus | `50000000.0` | Ethernet, Etherbone, SDCard, SPI SDCard, Video Terminal, Video Framebuffer, Video Colorbars | included |
| `terasic_de0nano` | terasic_de0nano | quartus | `50000000.0` | - | included |
| `terasic_de10lite` | terasic_de10lite | quartus | `50000000.0` | Video Terminal | included |
| `terasic_de10nano` | terasic_de10nano | quartus | `50000000.0` | - | included |
| `terasic_de1soc` | terasic_de1soc | quartus | `50000000.0` | - | included |
| `terasic_de2_115` | terasic_de2_115 | quartus | `50000000.0` | Ethernet, Etherbone, SDCard | included |
| `terasic_deca` | terasic_deca | quartus | `50000000.0` | Ethernet, Etherbone, SPI SDCard, Video Terminal | included |
| `terasic_sockit` | terasic_sockit | quartus | `50000000.0` | Video Terminal | included |
| `tinyfpga_bx` | tinyfpga_bx | icestorm | `16000000.0` | - | included |
| `trellisboard` | trellisboard | trellis | `75000000.0` | Ethernet, SDCard, SPI SDCard, Video Terminal, Video Framebuffer | included |
| `trenz_c10lpek` | trenz_c10lpek | quartus | `50000000.0` | - | included |
| `trenz_c10lprefkit` | trenz_c10lprefkit | quartus | `50000000.0` | Ethernet, Etherbone | included |
| `trenz_cr00010` | trenz_cr00010 | quartus | `50000000.0` | SPI Flash | included |
| `trenz_cyc1000` | trenz_cyc1000 | quartus | `50000000.0` | - | included |
| `trenz_max1000` | trenz_max1000 | quartus | `50000000.0` | - | included |
| `trenz_mega65` | trenz_mega65 | vivado | `100000000.0` | Ethernet, Etherbone | included |
| `trenz_mf001_intel` | trenz_mf001_intel | quartus | `116000000.0` | - | included |
| `trenz_mf_c10lp_001` | trenz_mf_c10lp_001 | quartus | `80000000.0` | - | included |
| `trenz_mf_max10_001` | trenz_mf_max10_001 | quartus | `116000000.0` | - | included |
| `trenz_s7mini` | trenz_s7mini | vivado | `100000000.0` | - | included |
| `trenz_smf2000` | trenz_smf2000 | libero_soc | `12000000.0` | - | included |
| `trenz_te0710` | trenz_te0710 | vivado | `100000000.0` | - | included |
| `trenz_te0711` | trenz_te0711 | vivado | `100000000.0` | - | included |
| `trenz_te0725` | trenz_te0725 | vivado | `100000000.0` | - | included |
| `trenz_te0741` | trenz_te0741 | vivado | `100000000.0` | - | included |
| `trenz_te0890` | trenz_te0890 | vivado | `100000000.0` | - | included |
| `trenz_tec0117` | trenz_tec0117 | gowin | `25000000.0` | SDCard, SPI SDCard | included |
| `trenz_tel0025` | trenz_tel0025 | radiant | `25000000.0` | SDCard, SPI SDCard, SPI Flash | included |
| `trenz_tem0006` | trenz_tem0006 | libero_soc | `12000000.0` | - | included |
| `tul_pynq_z2` | tul_pynq_z2 | vivado | `100000000.0` | - | included |
| `xilinx_ac701` | xilinx_ac701 | vivado | `100000000.0` | Ethernet, SPI Flash, PCIe | included |
| `xilinx_alveo_u200` | xilinx_alveo_u200 | vivado | `125000000.0` | PCIe | included |
| `xilinx_alveo_u250` | xilinx_alveo_u250 | vivado | `125000000.0` | PCIe | included |
| `xilinx_alveo_u280` | xilinx_alveo_u280 | vivado | `150000000.0` | PCIe | included |
| `xilinx_kc705` | xilinx_kc705 | vivado | `125000000.0` | Ethernet, SPI Flash, PCIe, SATA | included |
| `xilinx_kcu105` | xilinx_kcu105 | vivado | `125000000.0` | Ethernet, Etherbone, PCIe, SATA | included |
| `xilinx_kcu116` | xilinx_kcu116 | vivado | `125000000.0` | Ethernet, Etherbone, PCIe, SATA | included |
| `xilinx_kv260` | xilinx_kv260 | vivado | `100000000.0` | - | included |
| `xilinx_sp605` | xilinx_sp605 | ise | `54000000.0` | Video Terminal, Video Framebuffer, Video Colorbars | included |
| `xilinx_vc707` | xilinx_vc707 | vivado | `125000000.0` | PCIe | included |
| `xilinx_vcu118` | xilinx_vcu118 | vivado | `125000000.0` | - | included |
| `xilinx_vcu128` | xilinx_vcu128 | vivado | `125000000.0` | - | included |
| `xilinx_zc706` | xilinx_zc706 | vivado | `125000000.0` | Ethernet, Etherbone, PCIe | included |
| `xilinx_zcu102` | xilinx_zcu102 | vivado | `125000000.0` | - | included |
| `xilinx_zcu104` | xilinx_zcu104 | vivado | `125000000.0` | - | included |
| `xilinx_zcu106` | xilinx_zcu106 | vivado | `125000000.0` | PCIe | included |
| `xilinx_zcu216` | xilinx_zcu216 | vivado | `100000000.0` | - | included |
| `xilinx_zybo_z7` | digilent_zybo_z7 | vivado | `125000000.0` | - | included |
| `ypcb_00338_1p1` | ypcb_00338_1p1 | vivado | `125000000.0` | PCIe | included |
| `ztex213` | ztex213 | vivado | `100000000.0` | SDCard, SPI SDCard | included |
