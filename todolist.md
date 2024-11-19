# Issues and things to do to make this proj work

---

## Data Handling

### Tiff file loading

- it will only really work for micromanager files, will need tweaks for other tiffs

### Efficient storage and processing

- memmap handles this well, but processing is slow
- Start using *Dask* to speed up processing with multithreading

---

## Segmentation

- Fix Display issues, brightness fluctuates in openCV, but not in imageJ
    - This could be due to some averaging in the x,y,z resolutions?
    - this could also be due to normalization or data conversion issues!
- Stardist segmentation is useless at the moment
    - again, due to normalization or datatype problems is likely
    - this could also be due to the fact that the brightness fluctuates so much in python vs imageJ

---

## Tracking

- use graph based method to register the same cells over long time periods