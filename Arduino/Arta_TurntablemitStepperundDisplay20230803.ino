#include <Ethernet.h>
#include <EthernetUdp.h>
#include <Wire.h>  // Wire Bibliothek hochladen
#include <LiquidCrystal_I2C.h> // Vorher hinzugefügte LiquidCrystal_I2C Bibliothek hochladen
#include <AccelStepper.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);  //Hier wird das Display benannt (Adresse/Zeichen pro Zeile/Anzahl Zeilen)

//define Pins for Stepper Interface
#define dirPin 5
#define stepPin 2
#define motorInterfaceType 1
#define EnPin 8

// Create a new instance of the AccelStepper class:
AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

//technical data for the turntable
//float Ballbearingteeth = 176;
//float Pinionteeth = 12;
//float stepspermotorrotation = 1600;
//float stepperspeed = 1; //Drehgeschwindigkeit  Wert in ms 

int Index;
//variable fuer counter
int count = 0;
int Position1;
int Position2;
int Nullposition;
float Stepsprograd = 65.75;

String line0 = "FM Audio";
String line1 = "ARTA Turntable";
String line2 = "";
String line3 = "";
String position;

//Pin für den Naeherungssensor definieren
#define Referenzpunkt 3

//    NETZWERK

// Enter a MAC address and IP address for your controller below.
// The IP address should match your local network:
byte mac[] = { 0xB8, 0x96, 0x74, 0x01, 0x02, 0x03 };
unsigned int localPort = 10049;      // local port to listen on

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  // buffer to hold incoming packet,
char ReplyBuffer[UDP_TX_PACKET_MAX_SIZE];        // a string to send back

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;


// verschiedene Funktionen die verwendet werden


void lcdwriteline (int line,String Text){
  lcd.setCursor(0,line); //Text soll beim ersten Zeichen  in Reihe  line beginnen..
  lcd.print("                    ");
  delay(110);
  unsigned int StringLength = Text.length();
  int position = (20 - StringLength)/2;
  int cursor = (int)position;
  lcd.setCursor(cursor,line);
  lcd.print(Text);
  }

void referenzfahrt() {

  Serial.println("Fahre Turntable in Reset Position");
  lcdwriteline(3,"Fahre Referenz");
  
  if (digitalRead(Referenzpunkt) == HIGH) {

    stepper.setSpeed(500);
    while(digitalRead(Referenzpunkt) == HIGH) {  //While loop that SHOULD end if the input goes LOW
      //fahren 
      stepper.runSpeed();
    }
    Position1 = stepper.currentPosition();
  }

  if (digitalRead(Referenzpunkt) == LOW) {
    //in die entgegengesetzte Richtung fahren
    stepper.setSpeed(-500);
    while(digitalRead(Referenzpunkt) == LOW) {  //While loop that SHOULD end if the input goes HIGH
      //fahren
      stepper.runSpeed();
    }
    Position1 = stepper.currentPosition();

    //rechtsrum fahren
    stepper.setSpeed(500);

    while(digitalRead(Referenzpunkt) == HIGH) {  //While loop that SHOULD end if the input goes LOW
      //fahren
      stepper.runSpeed();
    }

    while(digitalRead(Referenzpunkt) == LOW) {  //While loop that SHOULD end if the input goes HIGH
      //fahren
      stepper.runSpeed();
    }
    Position2 = stepper.currentPosition();

    Nullposition = Position1 + ((Position2-Position1)/2);

    stepper.moveTo(Nullposition);
    stepper.runToPosition();
    delay(500);
    stepper.setCurrentPosition(0);
    stepper.disableOutputs();
    //end of if loop
    }

  
  lcdwriteline(3,"Am Referenzpunkt");
  Serial.println("Am Referenzpunkt angekommen.");

  }


void setup() {

// Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  //Display initialisieren und ersten Text schreiben 
  lcd.init(); //Im Setup wird der LCD gestartet
  lcd.backlight(); //Hintergrundbeleuchtung einschalten (0 schaltet die Beleuchtung aus).
  lcdwriteline(0,line0);
  lcdwriteline(1,line1);
  lcdwriteline(2,"Wait for DHCP");

  //Pin für den Naeherungssensor definieren
  pinMode(Referenzpunkt, INPUT_PULLUP); //Enable

  // start the Ethernet
  if (Ethernet.begin(mac) == 0)
  {
    Serial.println("DHCP Failed, using fixed IP");
    IPAddress ip(165, 166, 167, 100);
    Ethernet.begin(mac, ip);
    lcdwriteline(3,"DHCP FAILED");
    lcdwriteline(2,"FIXIP: 165.166.167.100");
  }
  else
  {
    Serial.println("Arduino connected to network using DHCP");
    //IP auf dem Display ausgeben
    char myIpString[24];
    IPAddress myIp = Ethernet.localIP();
    sprintf(myIpString, "%d.%d.%d.%d", myIp[0], myIp[1], myIp[2], myIp[3]);
    String myIps = "IP "+String(myIpString);
    lcdwriteline(2,myIps);
    line3 = myIps;
  }
  delay(1000);

  // start UDP
  Udp.begin(localPort);

  stepper.setMaxSpeed(500); //SPEED = Steps / second
  stepper.setAcceleration(1000); //ACCELERATION = Steps /(second)^2
 
  stepper.disableOutputs(); //disable outputs, so the motor is not getting warm (no current)

  
  //Referenzfahrt starten
  referenzfahrt();
}

void loop() {


  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();

  if (packetSize) {
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remote = Udp.remoteIP();
    for (int i=0; i < 4; i++) {
      Serial.print(remote[i], DEC);
      if (i < 3) {
        Serial.print(".");
      }
    }
    
    // read the packet into packetBuffer
    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    
    long steppaction = atol(packetBuffer);

    Serial.println("Wert steppaction");
    Serial.print(steppaction);

    delay(1000);

    
    float Pos = steppaction * Stepsprograd;
    int Position = (int)Pos;
    stepper.moveTo(Position);
    stepper.runToPosition();
    delay(1000);
    String acpos = String(steppaction);
    position = "Position: "+acpos+" Grad";
    lcdwriteline(3,position);
    delay(1000);
    stepper.disableOutputs();
    // Define String
    String reply = "Fahre Turntable auf Position "+String(steppaction)+" Grad";
    // Length (with one extra character for the null terminator)
    int reply_len = reply.length() + 1;
    // Prepare the character array (the buffer)
    ReplyBuffer[reply_len];
    // Copy it over
    reply.toCharArray(ReplyBuffer, reply_len);

    Serial.println("");
    Serial.println("");
    
    for(int i=0;i<UDP_TX_PACKET_MAX_SIZE;i++) packetBuffer[i] = 0;

    // send a reply to the IP address and port that sent us the packet we received
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write(ReplyBuffer);
    Udp.endPacket();

    
  
  delay(10);
  }

}

