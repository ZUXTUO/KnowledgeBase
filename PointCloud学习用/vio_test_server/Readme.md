use colmap-3.6




<br><br>
./VIO_Localization_Server-x86_64.AppImage server database.db ./sparse/ VocIndex.bin 8080
<br><br>
./VIO_Localization_Server-x86_64.AppImage save database.db ./sparse/ SavedMap.dat keyframes.txt
<br><br>
./VIO_Localization_Server-x86_64.AppImage index database.db ./sparse/ VocIndex.bin ../vocab/vocab_tree_flickr100K_words1M.bin
<br><br>