// adapted from https://github.com/beltoforion/kalstar/blob/master/kalstar.py
// documentation at https://stellarium.org/doc/0.20/

// Bug: stellarium can only run scripts that are copied into or symlinked from
//      /usr/share/stellarium/scripts
// invoke with:
//    stellarium --startup-script scriptname.ssc
// nb screenshots are stored in /home/alex/Pictures/Stellarium/
// and it won't overwrite existing screenshots

// convert screenshots to video with
//   for x in `seq -f %03.0f 0 999`; do mv frame_$x.png frame_0$x.png; done
//   ffmpeg -f image2 -r 25 -i frame_%4d.png outfile.mp4
//   (25 = frames per second)

// runtime of Stellarium is about 140 frames/min
// or just under an hour to generate the 7500 frames needed for 5 min at 25fps

// Author of original script: Ingo Berg
    // Version: 1.0
    // License: Public Domain
    // Name: Kaleidoskop Sternenhimmel
    // Description: Berechnung des Sternenhimmels

// Modified by Alexander Hanysz, September 2020

    param_frame_folder = "/home/alex/midi/python_animations/lullaby_stellarium_scripts/test_images"
    // apparently ignored: it's putting screen shots in /home/alex/Pictures/Stellarium/frame_nnn.png, and then frame_nnnn.png from frame 1000 onwards
    param_az = 270 // azimuth in degrees: 0=north, 90=east, etc
    param_alt = 20 // altitude in metres
    param_lat = 55.7562777778 // 55°45'22.6"N as a decimal
    param_long = 37.6039166667 // 37°36'14.1"E
    param_title = "Title goes here"
    param_date = "1872:12:14T12:30:00" // remember Moscow is GMT+3, so 12:30 is 3:30pm
    param_timespan = 18 // number of hours to simulate: later change to 17
    param_fov = 70 // default value from Python script, not sure what "field of view" is measuring here
    param_dt = 9.0629 // time between frames in seconds
    
    function makeVideo(date, file_prefix, caption, hours, long, lat, alt, azi)
    {
        core.setDate(date, "utc");
        core.setObserverLocation(long, lat, 425, 1, "Freiberg", "Earth");
        core.wait(0.5);
        core.moveToAltAzi(alt, azi)
        core.wait(0.5);
        //label = LabelMgr.labelScreen(caption, 70, 40, false, 40, "#aa0000");
        //LabelMgr.setLabelShow(label, true);
        //labelTime = LabelMgr.labelScreen("", 70, 90, false, 25, "#aa0000");
        //LabelMgr.setLabelShow(labelTime, true);
        core.wait(0.5);
        max_sec = hours * 60 * 60
        for (var sec = 0; sec < max_sec; sec += param_dt) {
            core.setDate('+' + param_dt + ' seconds');
            //LabelMgr.setLabelText(labelTime, core.getDate(""));
            core.wait(0.1);
            core.screenshot(file_prefix);
        }
        //LabelMgr.deleteAllLabels();
    }
    core.setTimeRate(0); 
    core.setGuiVisible(false);
    core.setMilkyWayVisible(true);
    core.setMilkyWayIntensity(4);
    SolarSystem.setFlagPlanets(true); // do not change: without the sun, it's always night-time!
    SolarSystem.setFlagLabels(false); // added
    SolarSystem.setMoonScale(12); // changed by Alex from 6 to 12
    SolarSystem.setFlagMoonScale(true);
    SolarSystem.setFontSize(25);
    
    StelSkyDrawer.setAbsoluteStarScale(1.5);
    StelSkyDrawer.setRelativeStarScale(1.65);
    StarMgr.setFontSize(20);
    StarMgr.setLabelsAmount(0); // changed by Alex from 3 to 0
    ConstellationMgr.setFlagLines(false); // changed by Alex
    ConstellationMgr.setFlagLabels(false); // changed by Alex
    ConstellationMgr.setArtIntensity(0.1);
    ConstellationMgr.setFlagArt(true);
    ConstellationMgr.setFlagBoundaries(false);
    ConstellationMgr.setConstellationLineThickness(3);
    ConstellationMgr.setFontSize(18);
    //LandscapeMgr.setCurrentLandscapeName("Hurricane Ridge");
    LandscapeMgr.setFlagAtmosphere(true);
    LandscapeMgr.setFlagLandscape(false); // added
    LandscapeMgr.setFlagCardinalsPoints(false); // added
    StelMovementMgr.zoomTo(param_fov, 0);
    core.wait(0.5);
    makeVideo(param_date, "frame_", param_title, param_timespan, param_long, param_lat, param_alt, param_az)
    core.screenshot("final", invert=false, dir=param_frame_folder, overwrite=true);
    core.setGuiVisible(true);
    core.quitStellarium();
