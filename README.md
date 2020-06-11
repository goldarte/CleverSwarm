# clever-show

[Русская версия](README_RU.md)

Software for making the drone show with drones controlled by [Raspberry Pi](https://www.raspberrypi.org/) with COEX [Clover](https://github.com/CopterExpress/clover) package and flight controller with [PX4](https://github.com/PX4/Firmware) firmware.

Create animation in [Blender](https://www.blender.org/), convert it to drone paths, set up the drones and run your own show!

[![Build Status](https://travis-ci.org/CopterExpress/clever-show.svg?branch=master)](https://travis-ci.org/CopterExpress/clever-show)

## Demo video

[![Autonomous drone show in a theater](http://img.youtube.com/vi/HdHbZFz7nR0/0.jpg)](http://www.youtube.com/watch?v=HdHbZFz7nR0)

12 drones perform in a show in Electrotheatre Stanislavsky, Moscow.

## This software includes

* [Drone side](drone/) for remote synchronized control of drones with emergency drone protection module
* [Server side](server/) for making the drone show with ability of tuning drones, animation and music
* [Blender 2.8 addon](blender-addon/) for exporting animation to drone paths
* [Raspberry Pi image](https://github.com/CopterExpress/clever-show/releases/latest) for quick launch software on the drones

## Documentation

> Documentation is available only in Russian for now.

Start tutorial is located [here](docs/ru/start-tutorial.md).

Detailed documentation is located in the [docs](docs/) folder.
