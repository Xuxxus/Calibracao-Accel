import os
import math
import pandas
import serial

# Defina a porta COM do Arduino (pode variar dependendo do seu sistema)
MAX_MEAS = 200  # max number of readings in the session, so that we don't create an infinite loop
AVG_MEAS = 25  # for each reading, take this many measurements and average them
SER_PORT = 'COM14'  # serial port the device is connected to
SER_BAUD = 115200  # serial port baud rate
FILENAME = os.path.join(os.getcwd(), 'acceldata.txt')  # output file



# Configuração da comunicação serial
ser = serial.Serial(SER_PORT, baudrate=115200)

def RecordDataPt(ser) -> tuple:

        ax = ay = az = 0.0

        for _ in range(AVG_MEAS):
                # read data
                try:
                    # Lê uma linha da porta serial
                    linha = ser.readline().decode('latin-1').strip()
                    if linha:
                        # Divida a linha em uma lista usando a vírgula como separador
                        data = linha.split(',')
                    
                        # Imprima os valores individuais
                        for valor in data:
                            ax_str = data[0]
                            ay_str = data[1]
                            az_str = data[2]

                            # Remover caracteres não numéricos e manter apenas dígitos e ponto decimal
                            ax_join = ''.join(caractere for caractere in ax_str if caractere.isdigit() or caractere == '.' or caractere == '-')
                            ay_join = ''.join(caractere for caractere in ay_str if caractere.isdigit() or caractere == '.' or caractere == '-')
                            az_join = ''.join(caractere for caractere in az_str if caractere.isdigit() or caractere == '.' or caractere == '-')

                            # Converter a string limpa em um valor de ponto flutuante
                            ax_now = float(ax_join)
                            ay_now = float(ay_join)
                            az_now = float(az_join)
                except:
                    ser.close()
                    raise SystemExit("[ERROR]: Error reading serial connection.")
                ax += ax_now
                ay += ay_now
                az += az_now
        return (round((ax / AVG_MEAS),6), round((ay / AVG_MEAS),6), round((az / AVG_MEAS),6))


def List2DelimFile(mylist: list, filename: str, delimiter: str = ',', f_mode='a') -> None:
    """Convert list to Pandas dataframe, then save as a text file."""
    df = pandas.DataFrame(mylist)
    df.to_csv(
        filename,  # path and filename
        sep=delimiter,
        mode=f_mode,
        header=False,  # no col. labels
        index=False  # no row numbers
    )


def main():
    data = []  # data list

    print('[INFO]: Place sensor level and stationary on desk.')
    input('[INPUT]: Press any key to continue...')
    # take measurements
    for _ in range(MAX_MEAS):
            user = input(
                    '[INPUT]: Ready for measurement? Type \'m\' to measure or \'q\' to save and quit: ').lower()
            if user == 'm':
                    # record data to list
                    ax, ay, az = RecordDataPt(ser)
                    magn = math.sqrt(ax**2 + ay**2 + az**2)
                    print('[INFO]: Avgd Readings: {:.4f}, {:.4f}, {:.4f} Magnitude: {:.4f}'.format(
                        ax, ay, az, magn))
                    data.append([ax, ay, az])
            elif user == 'q':
                    # save, then quit
                    print('[INFO]: Saving data and exiting...')
                    List2DelimFile(data, FILENAME, delimiter='\t')
                    ser.close()
                    print('[INFO]: Done!')
                    return
            else:
                    print('[ERROR]: \'{}\' is an unknown input. Terminating!'.format(user))
                    List2DelimFile(data, FILENAME, delimiter='\t')
                    ser.Close()
                    return
    # save once max is reached
    print('[WARNING]: Reached max. number of datapoints, saving file...')
    List2DelimFile(data, FILENAME, delimiter='\t')
    ser.Close()
    print('[INFO]: Done!')

if __name__ == '__main__':
    main()           




