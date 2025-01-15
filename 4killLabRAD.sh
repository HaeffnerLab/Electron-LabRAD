#!/bin/bash

kill $(ps aux | grep '[l]abrad' | awk '{print $2}')