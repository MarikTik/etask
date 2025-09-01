
#include "global/global.hpp"
#include "channels/external_channel.hpp"

void setup() {
    
}

void loop(){
    global::external_channel.update();
}

int main() {
    
    setup();
    while (true) loop();
    return 0;
}