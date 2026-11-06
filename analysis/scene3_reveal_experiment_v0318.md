# Révélation de la troisième scène sur V318

La lecture de la VRAM pendant deux boucles de démarrage montre un retard
du transfert des masques de la troisième scène. En NTSC, le premier octet
du masque change à l’image 3651 sur SMS et à 3653 sur Mega Drive.
En PAL, ces changements commencent aux images 3640 et 3641.

Un essai avance ce travail en conservant les attentes logiques après les
masques. Sur 14 000 images sans entrée par région, le nombre de pixels
différents de la SMS passe de 147 429 à 130 939 en NTSC, et de 124 148 à
127 264 en PAL. L’essai améliore 29 830 pixels et en dégrade 13 340 en NTSC.
En PAL, il en améliore 9 258 et en dégrade 12 374.

Le déplacement des attentes ne suffit donc pas à reproduire les transferts
partiels visibles pendant le balayage. Les octets de motifs observés et
les images émises sont mesurés séparément. La ROM de cet essai est conservée
dans l’archive avec ses sources et ses résultats. La version de jeu reste
la V318.

[Sources, ROM et mesures de l’essai](scene3-reveal-experiment-v0318/manifest.json)
