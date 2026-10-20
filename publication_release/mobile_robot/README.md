# Mobile robot integration

`main.py` dispatches CR10 robot commands, Trans200 AGV commands, and the named `photocatalysis` transfer workflow. Reusable device clients are under `devices/`; workflow ordering is under `workflows/`.

Install root dependencies and run from **this directory**:

```powershell
python main.py --help
python -m unittest discover -s tests -v
```

Physical command examples after deployment configuration:

```powershell
python main.py robot state
python main.py robot run-script pipetting
python main.py agv list-markers
python main.py workflow photocatalysis
```

Network/robot commands connect to real equipment. Robot-side programs, marker/mission definitions, and AGV maps must already exist on the controllers. Names and endpoint examples are in `devices/config.py`. The supplied workflow uses the `pipetting` and `photocatalytic` robot programs and named AGV operations.

The hub's legacy `--func mobile_*`/rack-transfer command set is not implemented by this CLI. A validated adapter plus the missing device-side transfer assets are required before claiming end-to-end integration. See `../docs/HARDWARE.md`.
