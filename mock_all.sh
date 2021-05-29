#!/bin/bash
killbg() {
        for p in "${pids[@]}" ; do
                kill "$p";
        done
}
trap killbg EXIT
pids=()
pipenv run python mock_services/mock_web3.py -s & 
pids+=($!)
pipenv run python mock_services/mock_pricefeed.py & 
pids+=($!)
pipenv run python mock_services/mock_status.py & 
pids+=($!)

pipenv run python mock_services/mock_validator.py


