void setup() 
{
  Serial.begin(115200);
}

// serial command buffer
char buf[255];
char out[255];
int buf_offset = 0;

void loop() 
{
  int totalBytes = Serial.available();
  if(totalBytes > 0) // check to see if data is present
  {
    while(totalBytes > 0) // start loop with number of bytes
    {
      char c = (char)Serial.read(); // read next byte
      if(c == '\n')
      {
        buf[buf_offset] = '\0'; // null terminator
        // process data
        //Serial.println(buf);
        char *str = strtok(buf," ,"); //str = roll,pitch,throttle,yaw
        strcat(out,"Flag: ");
        while (str != NULL) // loop to print out each token 
        {
          //Serial.println(str);
          strcat(out,str);
          strcat(out,", ");
          str = strtok(NULL," ,");  
        }
        out[strlen(out)-2] = '\0';
        Serial.println(out);
        buf_offset = 0;
      }
      else // when newline is reached
      {
        buf[buf_offset++] = c; // store in buffer and continue until newline is found
      }
      
      totalBytes--;
      out[0] = '\0';
    }
    //Serial.println("Garbage");
  }
}

