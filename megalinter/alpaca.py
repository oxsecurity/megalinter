#!/usr/bin/env python3
# flake8: noqa
from megalinter import config


# pylint: disable=E1111
def alpaca(request_id: str | None = None):
    print_alpaca = config.get(request_id, "PRINT_ALPACA", "true") == "true"
    if not print_alpaca:
        return

    print(
        """
    .:oool'                                  ,looo;                           
    .xNXNXl                                 .dXNNXo.                          
     lXXXX0c.                              'oKXXN0;                           
     .oKNXNX0kxdddddddoc,.    .;lodddddddxk0XXXX0c                            
      .:kKXXXXXXXXXXXXNXX0dllx0XXXXXXXXXXXXXXXKd,                             
        .,cdkOOOOOOOO0KXXXXXXXXXXK0OOOOOOOkxo:'                               
                      'ckKXNNNXkc'                                            
              ':::::;.  .c0XX0l.  .;::::;.                                    
              'xXXXXXx'   :kx:   ;OXXXXKd.                                    
               .dKNNXXO;   ..   :0XXXXKl.                                     
                .lKXXXX0:     .lKXXXX0:                                       
                  :0XXXXKl.  .dXXXXXk,                                        
                   ;kXXXXKd:cxXXXXXx'                                         
                    'xXNXXXXXXXXXKo.                                          
                     .oKXXXXNXXX0l.                                           
                      .lKNNXNNXO:                                             
                        ,looool'                                              

==========================================================
=============   MegaLinter, by OX.security   =============
=========  https://ox.security?ref=megalinter  ===========
==========================================================
"""
    )
    return True
