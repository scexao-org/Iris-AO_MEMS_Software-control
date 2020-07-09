################################################################################
##################           Show output messages           ####################
################################################################################

import zmq

################################################################################
##################           Communication process          ####################
################################################################################

if __name__ == "__main__":
    # Prepare our context
    context = zmq.Context()

    # Socket to receive messages on
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5551")
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    while True:
        # Read envelope with address
        contents = subscriber.recv_string()
        # contents_UTF = contents.decode('UTF-8')

        if contents == "done()":
            break
        else:
            print(contents)

    # To finish the process and exit
    subscriber.close()
    context.term()