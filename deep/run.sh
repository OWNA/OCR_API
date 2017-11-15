set -x

# Char CNN
python -m deep.charcnn.train --num_layers 2 --num_channels 64 --hidden_size 256 --max_char 6 --learning_rate 0.01
python -m deep.charcnn.train --num_layers 4 --num_channels 64 --hidden_size 256 --max_char 6 --learning_rate 0.01
python -m deep.charcnn.train --num_layers 5 --num_channels 64 --hidden_size 256 --max_char 6 --learning_rate 0.01
python -m deep.charcnn.train --num_layers 5 --num_channels 64 --hidden_size 512 --max_char 6 --learning_rate 0.01
python -m deep.charcnn.train --num_layers 5 --num_channels 64 --hidden_size 256 --max_char 10 --learning_rate 0.01
python -m deep.charcnn.train --num_layers 6 --num_channels 64 --hidden_size 256 --max_char 6 --learning_rate 0.01

# Basic RNN
python -m deep.basicrnn.train --num_layers 2 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=16 --learning_rate 0.001
python -m deep.basicrnn.train --num_layers 4 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=16 --learning_rate 0.005
python -m deep.basicrnn.train --num_layers 4 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.005
python -m deep.basicrnn.train --num_layers 5 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=16 --learning_rate 0.005
python -m deep.basicrnn.train --num_layers 5 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
python -m deep.basicrnn.train --num_layers 6 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=16 --learning_rate 0.01

# CTC RNN
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 2 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=16 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 2 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 2 --num_channels 128 --time_dense_size 512 --rnn_size 512 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 3 --num_channels 128 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 3 --num_channels 128 --time_dense_size 512 --rnn_size 512 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 4 --num_channels 128 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 2 --rnn_num_layers 4 --num_channels 128 --time_dense_size 512 --rnn_size 512 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 3 --rnn_num_layers 2--num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
python -m deep.ctcrnn.train --conv_num_layers 4 --rnn_num_layers 2 --num_channels 64 --time_dense_size 256 --rnn_size 256 --attention_size=0 --learning_rate 0.01
