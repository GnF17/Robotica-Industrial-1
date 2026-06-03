% 1. Conecta ao Arduino 
placa = arduino('COM3', 'Uno');

% 2. Define os pinos digitais 
motor_base = {'D2', 'D3', 'D4', 'D5'};
motor_braco1= {'D6', 'D7', 'D8', 'D9'};
motor_braco2 = {'D10', 'D11', 'D12', 'D13'};

% 3. Sequência de 4 passos (Half-step, que garante mais suavidade)
step_seq = [
    [1 0 0 0];
    [1 1 0 0];
    [0 1 0 0];
    [0 1 1 0];
    [0 0 1 0];
    [0 0 1 1];
    [0 0 0 1];
    [1 0 0 1]
];

% 4. Controla o sentido e a velocidade do motor
delay = 0.002; % Tempo de pausa entre passos (ajusta a velocidade)
num_voltas = 2; % Quantidade de voltas (aproximadamente)

% O 28BYJ-48 tem cerca de 4096 passos por volta
passos_totais = 4096 * num_voltas; 

movimento(placa, motor_base, passos_totais,delay, step_seq);
movimento(placa, motor_braco1, passos_totais,delay, step_seq);
movimento(placa, motor_braco2, passos_totais,delay, step_seq);

% 5. Limpa a conexão ao terminar
clear placa;

function passo = movimento(placa, motor, passos_totais, delay, step_seq)

    for i = 1:passos_totais
        % Calcula qual passo da matriz deve ser ativado
        idx = mod(i - 1, 8) + 1;
        
        % Envia o sinal para os 4 pinos
        for p = 1:4
            writeDigitalPin(placa, motor{p}, step_seq(idx, p));
        end
        
        % Pausa para dar tempo do motor se mover
        pause(delay);
    end
end
