// codigo que almacene todo el buffer en un .txt 
// lo del doble internet +optimizar rasp + manejo de errores de comu + boton + control bien + 2da camara (AZUL) + ultras +
// mejorar vision cercano lejos + si es grande no es lata + poder imrpirmir su area y su color   
// el html que sepa si esta en inetrne false o true

#include <WiFi.h>
#include <WebSocketsServer.h>

const int b1 = 16;
const int b2 = 17;

const int in1 = 18;
const int in2 = 19;

const int in3 = 21;
const int in4 = 22;

int freq = 5000;
int resolution = 8;

float Kp = 4.5; 
int veloBANDA = 80 ; 
int velocidadBase = 155;

int velocidad = velocidadBase;
int velocidadizq = velocidadBase;

String respuesta = "";  

bool internet = true ; 

const char* ssid = "ESP32_CHAT";
const char* password = "12345678";

WebSocketsServer webSocket = WebSocketsServer(81);

void setup() {
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  

  webSocket.begin();
  webSocket.onEvent(handleWebSocketEvent);

 
  pinMode(b1, OUTPUT);
  pinMode(b2, OUTPUT);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  ledcAttach(b1, freq, resolution);
  ledcAttach(b2, freq, resolution);

  ledcAttach(in1, freq, resolution);
  ledcAttach(in2, freq, resolution);

  ledcAttach(in3, freq, resolution);
  ledcAttach(in4, freq, resolution);


  ledcWrite(b1, 0);
  ledcWrite(b2, 0);
  ledcWrite(in1, 0);
  ledcWrite(in2, 0);
  ledcWrite(in3, 0);
  ledcWrite(in4, 0);

}

void loop() {
    webSocket.loop();

    if (internet == false) {
      if (Serial.available()) {
        String mensaje = Serial.readStringUntil('\n');
        mensaje.trim();
      
        if (mensaje.length() > 0 && (isdigit(mensaje[0]) || mensaje[0] == '-')) {
        float error = mensaje.toFloat();
        int ajuste = error * Kp;
        int velocidad = velocidadBase + ajuste;
        int velocidadizq = velocidadBase - ajuste;

        velocidad = constrain(velocidad, 0, 255);
        velocidadizq = constrain(velocidadizq, 0, 255);

        
        MotorIzq(velocidadizq );
        MotorDer(velocidad);
         
        } else if (mensaje == "N") {
          Right(velocidadBase , velocidadBase ); 
        } else if (mensaje == "S") {
          STOP(velocidadBase , velocidadBase ); 
        } 

      }
    
    }
}

void handleWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  
  switch(type) {

    case WStype_CONNECTED:
      webSocket.sendTXT(num, "Bienvenido al servidor ESP32");
      break;

    case WStype_DISCONNECTED:
      break;

    case WStype_TEXT:

      String mensaje = String((char*)payload);
      respuesta = "Recibí tu letra: ";
      respuesta += mensaje; 
      webSocket.sendTXT(num, respuesta);
      
      respuesta = ""; 

      if(mensaje=="R" && internet ) {
        Right( velocidad , velocidadizq );
      }
      else if(mensaje=="L" && internet ) {
        Left( velocidad , velocidadizq );
      }
      else if(mensaje=="F" && internet ) {
        Forward( velocidad  , velocidadizq );
      }
      else if(mensaje=="B"&& internet  ) {
        Back( velocidad , velocidadizq );
      }
      else if(mensaje=="S" && internet ) {
        STOP( velocidad , velocidadizq );
      }
      else if(mensaje=="W"&& internet ) {
        UPVEL();  
      }
      else if (mensaje =="X" && internet ) {
        DOWNVEL();  
      }
      else if(mensaje=="P"&& internet ) {
        UPVELIZQ();  
      }
      else if (mensaje =="Ñ" && internet ) {
        DOWNVELIZQ();  
      }
      else if (mensaje =="K" && internet ) {
        KM();  
      }
      else if (mensaje =="k" && internet ) {
        Km();  
      }else if (mensaje =="J") {
        ForwardBANDA( veloBANDA );
      }
      else if (mensaje =="M") {
        STOPBANDA( veloBANDA );
      } 
      else if(mensaje=="Q") {
        UPVEL_BANDA();  
      }
      else if (mensaje =="A" ) {
        DOWNVEL_BANDA();  
      }
      else if(mensaje=="Y") {
        UPVEL_BASE();  
      }
      else if (mensaje =="T" ) {
        DOWNVEL_BASE();  
      }
      else if (mensaje =="Z") {
        internet = !internet ; 
        STOP( velocidad , velocidadizq  ); 
      }
      else {
        respuesta = "ERROR \n" ;
      }  
      webSocket.sendTXT(num, respuesta);  
      break;

  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////

void UPVEL(   ) {
  
        
        respuesta = "SUBIENDO_Velocidad a: " ;
        
        velocidad += 10 ;
        velocidad = constrain(velocidad, 0, 255); 
        
        respuesta += String(velocidad) + "\n" ; 
        
  
}

void DOWNVEL(  ) {
  
        
      respuesta = "Bajando_Velocidad a: " ;
      
      velocidad -= 10 ;
      velocidad = constrain(velocidad, 0, 255); 
      
      respuesta += String(velocidad) + "\n" ; 
        
}


void UPVELIZQ(   ) {
  
        
        respuesta = "SUBIENDO_Velocidad izq a: " ;
        
        velocidadizq += 10 ;
        velocidadizq = constrain(velocidadizq, 0, 255); 
        
        respuesta += String(velocidadizq) + "\n" ; 
        
  
}

void DOWNVELIZQ(  ) {
  
        
      respuesta = "Bajando_Velocidad  izq a: " ;
      
      velocidadizq -= 10 ;
      velocidadizq = constrain(velocidadizq, 0, 255); 
      
      respuesta += String(velocidadizq) + "\n" ; 
        
}

void KM(   ) {
  
        
        respuesta = "SUBIENDO_K a: " ;
        
        Kp += .1 ;
         
        
        respuesta += String(Kp) + "\n" ; 
        
  
}

void Km(  ) {
  
        
     respuesta = "BAJANDO_K a: " ;
        
        Kp -= .1 ;
         
        
        respuesta += String(Kp) + "\n" ; 
        
}

//////////////////////////////////////////////////////////////////////////////////////////////////////

void Forward(  int velocidad , int velocidadizq ) {
  
     
      respuesta = "32Forward: D" + String(velocidad)+"I" +String(velocidadizq) + "\n"; 
      
      MotorIzq(velocidadizq );
      MotorDer(velocidad);
      
      Serial.println("FORWARD"); 
  
}


void Back(int velocidad , int velocidadizq ) {
    
      respuesta = "32Back: " + String(velocidad) +"I" +String(velocidadizq) + "\n"; 
      
      MotorIzq(-velocidadizq );
      MotorDer(-velocidad);

      Serial.println("BACK");
  
}

void Right(int velocidad , int velocidadizq ) {
    
      respuesta = "32Right: " + String(velocidad)+"I" +String(velocidadizq) + "\n"; 
      
      MotorIzq(velocidadizq );
      MotorDer(-velocidad);

      Serial.println("RIGHT");
  
}


void Left(int velocidad , int velocidadizq ) {
  
      respuesta = "32Left: " + String(velocidad) +"I" +String(velocidadizq) + "\n"; 
      
      MotorIzq(-velocidadizq );
      MotorDer(velocidad);

      Serial.println("LEFT");
  
}

void STOP( int velocidad , int velocidadizq ) {
   
      respuesta = "32STOP: " + String(velocidad)+"I" +String(velocidadizq) + "\n"; 
      
      MotorIzq(0 );
      MotorDer(0);

      Serial.println("STOP");
  
}

//////////////////////////////////////////////////////////////////////////////////////////////////////

void MotorIzq(double pwm) {
  pwm = constrain(pwm, -255, 255);// resolucion 
 
  if (pwm >= 0) { 
    ledcWrite(in1,pwm); ledcWrite(in2,0); 
  }
  else { 
    ledcWrite(in1,0); ledcWrite(in2,-pwm);
  }
  
}

void MotorDer(double pwm) {
  pwm = constrain(pwm, -255, 255); // resolucion

  if (pwm >= 0) { 
    ledcWrite(in3,pwm); ledcWrite(in4,0); 
  }
  else { 
    ledcWrite(in3,0); ledcWrite(in4,-pwm); 
  }
} 



void UPVEL_BANDA(   ) {
  
        
        respuesta = "SUBIENDO_Velocidad BANDA a: " ;
        
        veloBANDA += 10 ;
        veloBANDA = constrain(veloBANDA, 0, 255); 
        
        respuesta += String(veloBANDA) + "\n" ; 

  
}

void DOWNVEL_BANDA(  ) {
  
        
      respuesta = "Bajando_Velocidad BANDA a: " ;
      
      veloBANDA -= 10 ;
      veloBANDA = constrain(veloBANDA, 0, 255); 
      
      respuesta += String(veloBANDA) + "\n" ; 
}


void ForwardBANDA(  int velocidad  ) {
  
     
      respuesta = "32activandoBANDAS:" + String(velocidad) + "\n"; 
      
      MotorBANDA(-velocidad);
      
      Serial.println("BANDAS"); 
  
}


void MotorBANDA(double pwm) {
  pwm = constrain(pwm, -255, 255); // resolucion

  if (pwm >= 0) { 
    ledcWrite(b1,pwm); ledcWrite(b2,0); 
  }
  else { 
    ledcWrite(b1,0); ledcWrite(b2,-pwm); 
  }
} 


void STOPBANDA( int velocidad ) {
   
      respuesta = "32StopBandas: " + String(velocidad) + "\n"; 
      
      MotorBANDA(0);

      Serial.println("STOP_BANDAS");
  
}


void UPVEL_BASE(   ) {
  
        
        respuesta = "SUBIENDO_Velocidad BASE a: " ;
        
        velocidadBase += 10 ;
        velocidadBase = constrain(velocidadBase, 0, 255); 
        
        respuesta += String(velocidadBase) + "\n" ; 

  
}

void DOWNVEL_BASE(  ) {
  
        
      respuesta = "Bajando_Velocidad BASE a: " ;
      
      velocidadBase -= 10 ;
      velocidadBase = constrain(velocidadBase, 0, 255); 
      
      respuesta += String(velocidadBase) + "\n" ; 
}
