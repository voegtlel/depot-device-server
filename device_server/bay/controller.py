from enum import Enum

from pydantic import BaseModel
from time import sleep

from smbus import SMBus


class Address(BaseModel):
    """ Address of the bay, containing the controller register and the bitmask. """

    controller_register: int = 0x0
    register_bit_mask: int = 0x0


class ControllerConfig(BaseModel):
    """ Configuration for a controller. """

    controller_id: str
    address: int
    i2c_port: int


class MP23016Registers(Enum):
    """ Register addresses of the IO expander. """

    GP0 = 0x0
    GP1 = 0x1
    OLAT0 = 0x2
    OLAT1 = 0x3
    IPOL0 = 0x4
    IPOL1 = 0x5
    IODIR0 = 0x6
    IODIR1 = 0x7
    INTCAP0 = 0x8
    INTCAP1 = 0x9
    IOCON0 = 0xA
    IOCON1 = 0xB


class Controller:
    """ Generic controller which contains the base information. """

    def __init__(self, controller_config: ControllerConfig):
        self.controller_id = controller_config.controller_id
        self.address = controller_config.address
        self.bus = SMBus(controller_config.i2c_port)

    def configure(self):
        """ Reset all registers to the default. """
        self.bus.write_byte_data(self.address, MP23016Registers.GP0.value, 0x00)
        self.bus.write_byte_data(self.address, MP23016Registers.GP1.value, 0x00)

        self.bus.write_byte_data(self.address, MP23016Registers.OLAT0.value, 0x00)
        self.bus.write_byte_data(self.address, MP23016Registers.OLAT1.value, 0x00)

        self.bus.write_byte_data(self.address, MP23016Registers.IPOL0.value, 0x00)
        self.bus.write_byte_data(self.address, MP23016Registers.IPOL1.value, 0x00)

        self.bus.write_byte_data(self.address, MP23016Registers.IPOL0.value, 0x00)
        self.bus.write_byte_data(self.address, MP23016Registers.IPOL1.value, 0x00)

        self.bus.write_byte_data(self.address, MP23016Registers.IODIR0.value, 0xff)
        self.bus.write_byte_data(self.address, MP23016Registers.IODIR1.value, 0xff)

        # Resolution of the interrupt precision. If 0bXXXXXXX0 then 200us else 32ms.
        self.bus.write_byte_data(self.address, MP23016Registers.IOCON0.value, 0x00)


class StateController(Controller):
    """ Controller which can read the state of the bays. """

    def is_open(self, address: Address) -> bool:
        """ Get the state of the given bay. """

        state_register = self.bus.read_byte_data(self.address, address.controller_register)

        # If the bit of the given port is set, then the door is closed.
        return state_register & address.register_bit_mask == 0


class ActuatorController(Controller):
    """ Controller which can open the bays. """

    def configure(self):
        """ Configure the setting registers. """
        super().configure()

        # Set all port to output ports.
        self.bus.write_byte_data(self.address, MP23016Registers.IODIR0.value, 0x00)
        self.bus.write_byte_data(self.address, MP23016Registers.IODIR1.value, 0x00)

    def open_bay(self, address: Address):
        """ Open the given register."""
        # UNSAFE: Unlock for a short period of time. If sleeping too long or interrupted, hardware may fail.
        # First make sure that all ports are "off".
        self.bus.write_byte_data(self.address, MP23016Registers.GP0.value, 0x0)
        self.bus.write_byte_data(self.address, MP23016Registers.GP1.value, 0x0)

        sleep(0.01)

        self.bus.write_byte_data(
            self.address,
            address.controller_register,
            address.register_bit_mask,
        )
        sleep(0.01)
        self.bus.write_byte_data(self.address, address.controller_register, 0x0)
