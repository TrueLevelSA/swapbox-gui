README
------

This project provides a lovely kivy interface for ATM4COIN

Dependencies
------------

Kivy 1.8.0
zbarcam
devilspie2


Setup Instructions
------------------

*   RaspberryPi (2 B+ recommended)
*   Olimex (A20 Micro recommended)



abel:
                    text: 'We Sell'
                    font_size: 30
                    color: 0,0,0,1
                    canvas:
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            rectangle: self.x,self.y,self.width,self.height
                            width: 1
                Label:
                    text: 'BTC'
                    font_size: 30
                    color: 0,0,0,1
                    canvas:
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            rectangle: self.x,self.y,self.width,self.height
                            width: 1