#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <stdlib.h>
#include "header.h"      //Header file for the Configuration Bits/
#include <pic18f4550.h>  //Header file PIC18f4550 definitions/
#define _XTAL_FREQ  8000000  //In order to be able to use the delay function/
#define RS LATE0              /* PORTD 0 pin is used for Register Select */
#define EN LATE1                       /* PORTD 1 pin is used for Enable */
#define led LATE2
#define ldata LATD                 /* PORTB is used for transmitting data to LCD */
#define in1 LATB3
#define in2 LATB2
#define in3 LATB1
#define in4 LATB0




void LCD_Init();
int ADC_Read(int channel);
void LCD_Clear();
void LCD_Command(char );
void LCD_Char(char x);
void LCD_String(const char *);
void LCD_String_xy(char ,char ,const char*);
void displayScrolling(char *);
void LCD_Init();
int count =0; 
void goBackward(int);
void goForward(int);
void goRight(int);
void goLeft(int);
void stop(void);
void turnRight(void);
void turnLeft(void);
void back(void);
void forward(void);


void main(void)
{       
    OSCCON=0x72;		/* Set internal oscillator to 8MHz*/
    TRISA=0xFF;
    TRISB=0x00;
    TRISD=0x00;
    TRISE=0x00;
    
    ADCON1 = 0x0E;	
    ADCON2 = 0x92;	
    ADRESH=0;		
    ADRESL=0;  
    
    LCD_Init();
    char s[50];
    int b0, b1, b2;
    
    while(1){
        b0= getValue(2);
        b1= getValue(3);
        b2 = getValue(4);
        LCD_Char(b0+48);
        LCD_Char(b1+48);
        LCD_Char(b2+48);

        if(b0==0 && b1==0 && b2 == 0){
            stop();
        }else if(b0==0 && b1==0 && b2 == 1){
            back();
        }else if (b0==0 && b1==1 && b2 == 0){
            turnRight();
        } else if (b0==0 && b1==1 && b2 == 1){
            turnLeft();
        }else{
            forward();
        }  
        LCD_Clear();
 

        }
        
    }
        


int getValue(int channel){
     float distance;
    int digital;
    digital = ADC_Read(channel);
        //distance = digital*1023;
	//Convert digital value into analog voltage/
       
        distance= digital*((float)5/(float)1023);  
        if(distance >3)
            return 1;
        return 0;
}
void forward(){
    in1 = 1;
    in2 =0;
    in3=1;
    in4=0;
    
}

void turnLeft(){
    in1 = 1;
    in2 =0;
    in3=0;
    in4=1;
}
void turnRight(){
    in1 = 0;
    in2 =1;
    in3=1;
    in4=0;
}
void stop(){
    in1 = 0;
    in2 =0;
    in3=0;
    in4=0;
}
void back(){
    in1 = 0;
    in2 =1;
    in3=0;
    in4=1;
}

void goForward(int n){
    if (n>5)
        n=5;
    forward();
    
    for (int i=0; i<n;i++){
        __delay_ms(10);
        led=1;
        __delay_ms(10);
        led=0;
    }
    stop();   
    
    }
void goBackward(int n){
    if (n>5)
        n=5;
    back();
     for (int i=0; i<n;i++){
        __delay_ms(10);
        led=1;
        __delay_ms(10);
        led=0;
    }
    stop();   
    
    }
void goLeft(int n){
    
    turnLeft();
     for (int i=0; i<n;i++){
        __delay_ms(10);
        led=1;
        __delay_ms(10);
        led=0;
    }
    stop();   
    
    }
void goRight(int n){
    
    turnRight();
     for (int i=0; i<n;i++){
        __delay_ms(10);
        led=1;
        __delay_ms(10);
        led=0;
    }
    stop();   
   
    }
void LCD_Init()
{
    
    LCD_Command(0x38);     /* uses 2 line and initialize 5*7 matrix of LCD */
    LCD_Command(0x01);     /* clear display screen */
    LCD_Command(0x0c);     /* display on cursor off */
    LCD_Command(0x06);     /* increment cursor (shift cursor to right) */
        
}

void LCD_Clear()
{
    	LCD_Command(0x01); /* clear display screen */
}

void LCD_Command(char cmd )
{
	ldata= cmd;            /* Send data to PORT as a command for LCD */   
	RS = 0;                /* Command Register is selected */
	EN = 1;                /* High-to-Low pulse on Enable pin to latch data */ 
    __delay_ms(1);
	EN = 0;
	__delay_ms(3);	
}

void LCD_Char(char dat)
{
	ldata= dat;            /* Send data to LCD */  
	RS = 1;                /* Data Register is selected */
	EN=1;                  /* High-to-Low pulse on Enable pin to latch data */   
    __delay_ms(1);
	EN=0;
	__delay_ms(1);
}


void LCD_String(const char *msg)
{
	while((*msg)!=0)
	{		
	  LCD_Char(*msg);
	  msg++;	
    	}
		
}

void LCD_String_xy(char row,char pos,const char *msg)
{
    char location=0;
    if(row<=1)
    {
        location=(0x80) | ((pos) & 0x0f); //Print message on 1st row and desired location/
        LCD_Command(location);
    }
    else
    {
        location=(0xC0) | ((pos) & 0x0f); //Print message on 2nd row and desired location/
        LCD_Command(location);    
    }  
    LCD_String(msg);

}
 
int ADC_Read(int channel)
{
    int digital;

    /* Channel 0 is selected i.e.(CHS3CHS2CHS1CHS0=0000) & ADC is disabled */
    ADCON0 =(ADCON0 & 0b11000011)|((channel<<2) & 0b00111100);  
    
    ADCON0 |= ((1<<ADON)|(1<<GO));	//Enable ADC and start conversion/

   
    while(ADCON0bits.GO_nDONE==1);

    digital = (ADRESH*256) | (ADRESL);	//Combine 8-bit LSB and 2-bit MSB/
    return(digital);
}