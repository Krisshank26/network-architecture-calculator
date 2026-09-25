import socket 
import json 
import datetime 
import asyncio 

async def __main__(): 
    
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM ) 
    
    print("TCP Socket has been created " ) 
    
    hostname= "127.0.0.1" 
    PORT= 8080 
    
    serversocket.bind((hostname, PORT ) ) 
    
    serversocket.listen(10 ) 
    
    # print("\r\n Here " ) 
    
    print(f"Socket is bound to Host: {hostname } and is Listening on PORT: {PORT } " ) 
    
    (sck, clientaddr )= serversocket.accept() 
    
    print("Client IP Address Is: ", clientaddr ) 
    
    timer= "" 
    
    try: 
        while True: 
        
            request= sck.recv(1024 ) 
            if timer!= "": 
                timer.cancel() 
                try: 
                    await timer 
                except asyncio.CancelledError: 
                    pass 
                timer= "" 
            timer= asyncio.create_task(start_timer(sck, clientaddr ) ) 
            print(timer ) 
            
            requestdc= request.decode(encoding= "utf-8" ) 
            
            if requestdc== "": 
                timer.cancel() 
                try: 
                    await timer 
                except asyncio.CancelledError: 
                    pass 
                timer= "" 
                sck.close() 
                (sck, clientaddr )= serversocket.accpet() 
                
                print("Client IP Address Is: ", clientaddr ) 
                
                continue 
            
            # print(requestdc.split('\r\n' ) ) 
            
            request_lines= requestdc.split("\r\n" ) 
            request_method= request_lines[0].split(" " ) 
            
            response= parseHeaders(request_lines ) 
            
            if (response != "" ): 
                sck.send(response ) 
                continue 
            
            response= parseMethod(request_method ) 
            # print(response ) 
            sck.send(response ) 
    except Exception as e : 
        response= errMessage(500, e ) 
        sck.send(response ) 
        raise 
    
async def start_timer(sck, clientaddr ): 
    await asyncio.sleep(65.0 ) 
    sck.close() 
    print(f"Connection to {clientaddr } has been closed " ) 
    
def parseHeaders(req ): 
    
    response= "" 
    num= 0 
    for line in req: 
        if line == "": 
            break 
        if num == 0: 
            num= 1 
            continue 
        header= line.split(":" ) 
        if (len(header )< 2 ) or (header[0]== "" ) or (header[1]== "" ): 
            response= errMessage(400, "Headers Are Not Correct Here " ) 
            break 
    
    return response 

def parseMethod(req ): 
    
    allowPath= ["/add", "/sub", "/mul", "/div" ] 
    if len(req )!= 3 : 
        response= errMessage(400, "Method Line is Invalid" ) 
    elif req[0] != "GET": 
        response= errMessage(405, "Only GET Method Allowed Here " ) 
    else: 
        if req[1] == "/": 
            response= successMessage(200, "Welcome to our Calculator ", req ) 
        elif (len(req[1] )== 0 ) or (req[1][0] != '/' ): 
            response= errMessage(400, "URL Is Invalid" ) 
        else: 
            path= req[1].split('?' ) 
            if (len(path ) != 2 ) or (path[0] == "/" ) or (path[1] == "" ): 
                response= errMessage(400, "URL Is Invalid" ) 
            elif path[0] not in allowPath: 
                response= errMessage(404, "Path Not Found " ) 
            else: 
                parameters= path[1].split('&' ) 
                if (len(parameters )!= 2 ) or (len(parameters[0] )< 3 ) or (len(parameters[1] )< 3 ) or (parameters[0][0: 2 ]!= "a=" ) or (parameters[1][0: 2 ]!= "b=" ): 
                    response= errMessage(400, "Parameters are not Valid" ) 
                else: 
                    a= parameters[0][2: (len(parameters[0] ) ) ] 
                    b= parameters[1][2: (len(parameters[1] ) ) ] 
                    ca= checkFloat(a ) 
                    cb= checkFloat(b ) 
                    if (ca== 1 ) or (cb== 1 ): 
                        response= errMessage(400, "Parameters Are Not Valid" ) 
                    else: 
                        ca= float(a ) 
                        cb= float(b ) 
                        # print(a, type(ca ) ) 
                        if path[0]== "/add": 
                            message= add(ca, cb ) 
                        elif path[0]== "/sub": 
                            message= sub(ca, cb ) 
                        elif path[0]== "/mul": 
                            message= mul(ca, cb ) 
                        else: 
                            if cb== 0.0: 
                                response= errMessage(400, "Cannot Divide By 0 Here " ) 
                                return response 
                            else: 
                                message= div(ca, cb ) 
                        response= successMessage(200, message, req ) 
    return response 
                    
def add(a, b ): 
    return (a+ b ) 

def sub(a, b ): 
    return (a- b ) 

def mul(a, b ): 
    return (a* b ) 

def div(a, b ): 
    return (a/ b ) 

def checkFloat(num ): 
    try: 
        float(num ) 
        return 0 
    except ValueError: 
        return 1 

def successMessage(code, message, req ): 
    
    codeMap= { 
              200: "OK" 
    } 
    
    status= f"{req[2] } {code } {codeMap[code ] }" 
    response= status 
    date= f"Date: {datetime.datetime.now() }" 
    host= f"Host: localhost" 
    content_type= f"Content-Type: application/json" 
    responseBody= { "message": message } 
    content_length= f"Content-Length: {len(json.dumps(responseBody ) ) }" 
    connection= f"Connection: keep-alive" 
    response= response+ f"\r\n{date }\r\n{host }\r\n{content_type }\r\n{content_length }\r\n{connection }\r\n\r\n{json.dumps(responseBody ) }\r\n" 
    response= response.encode() 
    return response 
    
def errMessage(code, message ): 
    
    codemap= { 
              400: "Bad Request", 
              404: "Not Found", 
              405: "Method Not Allowed", 
              200: "OK", 
              500: "Internal Server Error" 
    } 
    
    status= f"HTTP/1.1 {code } {codemap[code ] }\r\n" 
    response= status 
    date= f"Date: {datetime.datetime.now() }\r\n" 
    allow_methods= f"Allow: GET\r\n" 
    if code== 405: 
        response= response+ allow_methods 
    host= f"Host: localhost\r\n" 
    content_type= f"Content-type: application/json\r\n" 
    responseBody= { "message": message } 
    content_length= f"Content-Length: {len(json.dumps(responseBody ) ) }\r\n" 
    connection= f"Connection: keep-alive\r\n\r\n" 
    response= response+ host+ date+ content_type+ content_length+ connection 
    response= response+ (json.dumps(responseBody ) )+ "\r\n" 
    
    response= response.encode() 
    return response 
        
asyncio.run(__main__() ) 