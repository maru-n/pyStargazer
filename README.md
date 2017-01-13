# pyStargazer

## installation

```
pip install git+https://github.com/maru-n/pyStargazer.git 
```

## Setup of markers

- put all markers on ceiling without rotation.
- RIGHT direction of marker towards to X-axis of global coordinate.
- marker mapping data is python dictionary

```
# {marker_id: [x,y,z],,,}
marker_map = {
    24836: [0, 0, 0],
    25092: [1.5, 0, 0],
    24594: [0, -1.5, 0],
    24706: [1.5, -1.5, 0]
}
```

## Examples

https://github.com/maru-n/pyStargazer/tree/master/examples
