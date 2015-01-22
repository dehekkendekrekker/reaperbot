#!/bin/bash

rfkill unblock 0
rfkill unblock 1

sudo python2 reaperbot.py reaperbot
