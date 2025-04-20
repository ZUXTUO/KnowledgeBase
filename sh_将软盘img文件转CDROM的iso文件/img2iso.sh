mkdir iso
mkdir dist
cp floppy.img dist/floppy.img
mv floppy.img iso/floppy.img
genisoimage -quiet -V 'MYOS' -input-charset iso8859-1 -o dist/cdrom.iso -b floppy.img -hide floppy.img iso/
rm -R iso