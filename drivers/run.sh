#!/bin/bash

set -e


# model_path=models/udr_4_dims_correct_recv_rate/range0/model_to_serve_step_1504800
# model_path=models/udr_4_dims_correct_recv_rate/range0/model_step_1504800.ckpt
# model_path=models/model_for_real_net/from_scratch_seed_20/model_step_619200.ckpt
# model_path=models/model_for_real_net/from_scratch_seed_20/model_step_619200.ckpt
model_path=models/udr_7_dims_fix_val_reward/range0_queue50/model_step_252000.ckpt
# save_dir=test_constant_bw
# save_dir=test_train_env
# save_dir=test_rtt_9_new_model
save_dir=test_cc
src/experiments/test.py local --schemes "aurora" -t 11 \
    --uplink-trace tests/traces/2mbps --downlink-trace tests/traces/12mbps \
    --prepend-mm-cmds "mm-delay 50 mm-loss uplink 0.00" \
    --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args='packets=50'" \
    --data-dir ${save_dir} \
    --model-path ${model_path} \
    --aurora-save-dir ${save_dir} \
    --pyprogram /home/zxxia/.virtualenvs/aurora/bin/python
# --downlink-queue=droptail --downlink-queue-args='packets=10'
#     --model-path ./range0/model_to_serve_step_1504800 \
python src/analysis/plot.py --data-dir ${save_dir} --schemes "aurora"
python drivers/plot/plot_time_series.py \
    --log-file ${save_dir}/aurora_datalink_run1.log ${save_dir}/cubic_datalink_run1.log \
    --save-dir ${save_dir}
python drivers/plot/plot_log.py \
    --log-file ${save_dir}/aurora_emulation_log.csv \
    --save-dir ${save_dir}
# python /home/zxxia/pantheon/src/analysis/report.py --data-dir exp/ --schemes "aurora cubic"
pkill -9 iperf



# src/experiments/test.py local --schemes "cubic" -t 15\
#     --uplink-trace cubic_datalink_run2_mahimahi.log --downlink-trace tests/12mbps_ack.trace \
#     --prepend-mm-cmds "mm-delay 50" \
#     --data-dir exp
# src/analysis/analyze.py --data-dir exp


# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/zxxia/pantheon/third_party/aurora/src/core
# /home/zxxia/pantheon/third_party/aurora/src/app/pccserver recv 9000 > aurora_server_log.csv
# sleep 20
# pkill -f pccclient
# pkill -f pccserver
