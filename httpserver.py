#By Naama Iluz ID 212259204
import socket
import os
import datetime

# TO DO: set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 5
#PATH = r"C:\Users\Naama\Downloads\webroot\webroot"
PATH = os.getcwd() + r"\webroot"
REDIRECTION_DICTIONARY = "/blabla.html"
FORBIDDEN_FILE = "/cool.txt"
CALC =  "/calculate-next"

def check_numbers(url):
    url = url.split('?')
    list = []
    prev = ""
    number = ""
    for i in url[1]:
        if (i.isdigit() and (prev.isdigit() or prev == '.' or prev == '-')) or (i == '.' and prev.isdigit()) \
                or (i == '-' and not prev.isdigit()):
            number += i
        elif i.isdigit():
            number = i
        if (number != "" and not i.isdigit() and not i == '-' and not i == '.') or (number != "" and i == url[1][-1]):
            list.append(number)
            number = ""
        prev = i
    return list


def get_file_data(filename):
    """ Get data from file """
    if "imgs" in filename:   # need to read binary
        with open(filename, "br") as f:
            file_content = f.read()
    else:                    # need to read as str
        with open(filename, "r") as f:
            file_content = f.read()
    return file_content


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    if resource == '' or resource == '/':
        url = PATH + "\index.html"
    else:
        url = resource
    if FORBIDDEN_FILE == url:
        dt = datetime.datetime.now();
        client_socket.send("HTTP/1.1 403 Forbidden\r\nDate: {}\r\n\r\n".format(dt).encode())
        return
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if REDIRECTION_DICTIONARY == url:  # if request is "/blabla.html" - return 302 and "index.html"
        # TO DO: send 302 redirection response
        client_socket.send("HTTP/1.1 302 Found\r\nLocation: http:\\index.html\r\n".encode())
        return
    if url == CALC:
        client_socket.send("HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\n5".encode())
        return
    if PATH not in url and PATH.replace("\\", "/") not in url:
        url = url.replace("/", "\\")
        if ("jpg" in url or "ico" in url or "gif" in url) and "imgs" not in url:
            url += "\\imgs"
        url = PATH + url
    if not os.path.isfile(url) and not "calculate-area" in url:  # if the requested file not exists
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n404 Not Found".encode())
        return
    # TO DO: extract requested file tupe from URL (html, jpg etc)
    if "calculate-area" in url:
        numbers = check_numbers(url)
        if len(numbers) < 2:
            client_socket.send("HTTP/1.1 200 OK\r\n\r\nNaN".encode())
            return
        if float(numbers[0]) < 0 or float(numbers[1]) < 0:
            client_socket.send("HTTP/1.1 200 OK\r\n\r\nYou must enter positive numbers".encode())
            return
        client_socket.send("HTTP/1.1 200 OK\r\n\r\n{}".format(float(numbers[0])*float(numbers[1])/2).encode())
        return
    data = get_file_data(url)
    data_length = bytes(str(len(data)), 'utf-8')
    split_url = url.split(".")
    filetype = split_url[-1]
    if filetype == 'html':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\n\r\n".format(len(data))
        # TO DO: generate proper HTTP header
    elif filetype == 'jpg':
        http_header = b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: " + data_length + b"\r\n\r\n"
    elif filetype == 'js':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/javascript; charset=UTF-8\r\nContent-Length: {}\r\n\r\n".format(len(data))
    elif filetype == 'css':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {}\r\n\r\n".format(len(data))
    elif filetype == 'ico':
        http_header = b"HTTP/1.1 200 OK\r\nContent-Type: image/ico\r\nContent-Length: " + data_length + b"\r\n\r\n"
    elif filetype == 'gif':
        http_header = b"HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\nContent-Length: " + data_length + b"\r\n\r\n"
    http_response = http_header + data
    if type(http_response) == bytes:
        client_socket.send(http_response)
    else:
        client_socket.send(http_response.encode())


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    words = request.split("\r\n")
    words = words[0].split(" ")
    if len(words) == 3 and words[0] == "GET" and words[2] == "HTTP/1.1":
        return True, words[1]
    return False, ""


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    # client_socket.send(FIXED_RESPONSE.encode())

    while True:
        # TO DO: insert code that receives client request
        client_request = client_socket.recv(1024).decode()
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode())
            print('Error: Not a valid HTTP request')
            break

    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        try:
            handle_client(client_socket)
        except:
            print("timrout!")


if __name__ == "__main__":
    # Call the main handler function
    main()
