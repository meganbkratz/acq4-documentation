.. _userDevicesPipette:

Pipette Devices
===============

Provide extra, optionally automated, control for tracking and positioning pipette or electrode tips.

Configuration
-------------

The major configuration assumption is that the setup has a micromanipulator that holds a pipette, and the user should be able to point to a location in the camera module and have the pipette go there. This requires a stage device that controls the micromanipulator, and a pipette device that has the stage as a parent. Both of these are meant to be independent of the stage device that moves the microscope, so the device hierarchy might look like:

    * Stage
        * Microscope
            * Camera
    * Manipulator1
        * Pipette1
    * Manipulator2
        * Pipette2

Example Configuration:

::

    Pipette1:
        driver: 'Pipette'
        parentDevice: 'Manipulator1'      ## A separately defined stage device that controls a micromanipulator 
        scopeDevice: 'Microscope'
        searchHeight: 2*mm

Extra Configuration Options:

    * searchHeight: the distance to focus above the sample surface when searching for pipette tips. This
      should be about 1-2mm, emough to avoid collisions between the pipette tip and the sample during search.
      Default is 2 mm.
    * searchTipHeight: the distance above the sample surface to bring the (putative) pipette tip position
      when searching for new pipette tips. For low working-distance objectives, this should be about 0.5 mm less
      than *searchHeight* to avoid collisions between the tip and the objective during search.
      Default is 1.5 mm.
    * approachHeight: the distance to bring the pipette tip above the sample surface when beginning 
      a diagonal approach. Default is 100 um.
    * idleHeight: the distance to bring the pipette tip above the sample surface when in idle position
      Default is 1 mm.
    * idleDistance: the x/y distance from the global origin from which the pipette top should be placed
      in idle mode. Default is 7 mm.

Camera Window Interface
-----------------------

Microsope Dock:

    * *set surface*:  a single lonely button that the microscope adds to the camera window. Use it to mark the location of your sample surface.

Pipette Dock(s):

    * *set target*:  lets you click in the camera window to set the final destination for the pipette (usually a cell). The target is a point in 3D, so you do need to have access to the focus depth via your microscope stage or focus drive. 

    * *set center*: lets you click on the pipette in the camera window to recalibrate its location. 

    * *set orientation*: lets you click in the camera window to set the orientation of the pipette (see Pipette Calibration, below).

    * *search*:  causes the microscope to focus 2 mm (or the distance set by the searchTipHeight configuration value) above the sample surface and brings the pipette under the center of the objective based on its last known location. This assists in finding a new tip and recalibrating its position, and is intended to be done after replacing pipette tips

    * *above target*:  moves the pipette directly over its target (which should be set using *set target*), and about 50 um above the sample surface. This allows one last recalibration before going to the cell. This step may or may not be necessary depending on the accuracy of your manipulator

    * *approach*:  brings the pipette into axial alignment with its target, about 50 um (or the distance set by the approachHeight configuration value)above the surface. From here, the user should be able to manually drive the pipette diagonally directly to the target.

    * *target*:  brings the pipette directly to its target using a diagonal approach. 

Pipette Calibration
-------------------

#. Bring the pipette tip to the center of the camera view
#. Click *set center*, and then click on the tip of the pipette. 
#. Click *set orientation*, then move the pipette forward across the screen, and then rotate the orientation arrows such that the x-axis points directly to the new position of the pipette.
#. Drag the arrows by the handle at their origin to the new position of the tip, and un-click *set orientation*.
#. Try moving the pipette. If all is well, then a blue arrowhead should follow the tip around. If the y-axis motion (perpendicular to the pipette) is backward, then click *set orientation* again and reverse the direction of the y-axis.

The above orientation calibration should only need to be done once. After that, just use *set center* whenever you need to recalibrate the pipette position.
