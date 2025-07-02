#!/bin/bash
curl -X POST -F 'file=@documents/strategie.pdf' 192.168.30.73:5060 > layout_data/boxes.json