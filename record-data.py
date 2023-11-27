import os
import math
import pandas
import serial
import time

# variáveis globais
MAX_MEAS = 200  # número máximo de leituras por sessão, para evitar ler infinitamente
AVG_MEAS = 25  # média de valores de cada leitura
SER_PORT = 'COM20'  # porta serial conectada ao dispositivo
SER_BAUD = 115200  # baud rate
FILENAME = os.path.join(os.getcwd(), 'acceldata.txt')  # arquivo com valores de saída do acelerômetro


class SerialPort:
    #Create and read data from a serial port.

    def __init__(self, port, baud=9600):
        #Create and read serial data.
        if isinstance(port, str) == False:
            raise TypeError('port deve ser uma string.')

        if isinstance(baud, int) == False:
            raise TypeError('Baud rate deve ser um número inteiro.')

        self.port = port
        self.baud = baud

        # Initialize serial connection
        self.ser = serial.Serial(
            self.port, self.baud, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
        self.ser.flushInput()
        self.ser.flushOutput()

    def Read(self, clean_end=True) -> str:
        """
            Ler e decodificar uma string de dados da porta serial.
            Args:
                clean_end (bool): Remover os caracteres '\\r' e '\\n' da string.
                Comum se usado com a função Serial.println() no Arduino. Padrão verdadeiro.
            Returns:
                (str): Mensagem decodificada em utf-8.
                (errors): Caso haja caractere desconhecido, substitui com "?"
        """
        while True:
            # Aguardar um curto período antes de ler os dados
            time.sleep(0.01)
            self.ser.flushInput() #cria uma conexão serial
            bytesToRead = self.ser.readline() #leitura da linha
            line = bytesToRead.decode('utf-8', errors='replace')
            if '\n' in line: #se ele detectar uma quebra de linha
                bytes = self.ser.readline() #inicia uma nova leitura da linha com início correto

                decodedMsg = bytes.decode('utf-8', errors='replace')
                break

        if clean_end == True:
            decodedMsg = decodedMsg.rstrip()

        return decodedMsg

    def Close(self) -> None:
        """Fecha a conexão"""
        self.ser.close()


def RecordDataPt(ser: SerialPort) -> tuple:
    """grava as leituras da porta serial e retorna média delas"""
    ax = ay = az = 0.0

    for _ in range(AVG_MEAS):
        # inicia a leitura
        try:
            # Ler dados da porta serial uma vez



            # Agora, os dados após o caractere de nova linha serão lidos
            dados_str = ser.Read()
            data = dados_str.strip().split(',') #separa os valores por virgula da linha
            ax_now = float(data[0]) #valor do primeiro número contido na linha do -> eixo x
            ay_now = float(data[1]) #valor do primeiro número contido na linha do -> eixo y
            az_now = float(data[2]) #valor do primeiro número contido na linha do -> eixo z
        except:
            ser.Close() #fecha a conexão serial caso erro
            raise SystemExit("[ERRO]: Erro de leitura na conexão serial.")
        """Somatória dos valores dos eixos x, y, z"""
        ax += ax_now
        ay += ay_now
        az += az_now

    return ((ax / AVG_MEAS), (ay / AVG_MEAS), (az / AVG_MEAS)) #retorna a média


def List2DelimFile(mylist: list, filename: str, delimiter: str = ',', f_mode='a') -> None:
    """Converter lista para um dataframe Pandas e, em seguida, salvar como um arquivo de texto."""
    df = pandas.DataFrame(mylist)
    df.to_csv(
        filename,  # nome do arquivo
        sep=delimiter,
        mode=f_mode,
        header=False,  # no col. labels
        index=False  # no row numbers
    )


def main():
    ser = SerialPort(SER_PORT, baud=SER_BAUD)
    data = []  # data list

    print('[INFO]: Posicione o sensor no suporte')
    input('[INPUT]: Pressione qualquer tecla para continuar...')

    # take measurements
    for _ in range(MAX_MEAS):
        user = input(
            '[INPUT]: Digite \'m\' para medir ou \'q\' para salvar e sair: ').lower()
        if user == 'm':
            # grava os dados e transfere para a lista
            ax, ay, az = RecordDataPt(ser)
            magn = math.sqrt(ax**2 + ay**2 + az**2)
            print('[INFO]: Média de leituras: {:.4f}, {:.4f}, {:.4f} Magnitude: {:.4f}'.format(
                ax, ay, az, magn))
            data.append([ax, ay, az])
        elif user == 'q':
            # save, then quit
            print('[INFO]: Salvando dados e saindo do programa...')
            List2DelimFile(data, FILENAME, delimiter='\t')
            ser.Close()
            print('[INFO]: Feito!')
            return
        else:
            print('[ERRO]: \'{}\' é uma entrada desconhecida. Saindo do Programa!'.format(user))
            List2DelimFile(data, FILENAME, delimiter='\t')
            ser.Close()
            return

    # salvar quando o número máximo de leituras é atingido
    print('[WARNING]: Número máximo de leituras atingido por sessão, salvando arquivo...')
    List2DelimFile(data, FILENAME, delimiter='\t')
    ser.Close()
    print('[INFO]: Feito!')


if __name__ == '__main__':
    main()  

