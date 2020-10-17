from pydantic import BaseModel
from typing import Dict, List, Tuple

from .controller import StateController, ActuatorController, Address, ControllerConfig


class StationConfig(BaseModel):
    state_controllers: List[ControllerConfig]
    actuator_controllers: List[ControllerConfig]
    # bay_id,
    # state_controller_id,
    # state_controller_address.controller_register,
    # state_controller_address.register_bit_mask,
    # actuator_controller_id,
    # actuator_controller_address.controller_register,
    # actuator_controller_address.register_bit_mask,
    bays: List[Tuple[str, str, int, int, str, int, int]]


class Bay:
    bay_id: str
    state_controller: StateController
    state_controller_address: Address
    actuator_controller: ActuatorController
    actuator_controller_address: Address

    def __init__(
            self,
            bay_id: str,
            state_controller: StateController,
            state_controller_address: Address,
            actuator_controller: ActuatorController,
            actuator_controller_address: Address,
    ):
        self.bay_id = bay_id
        self.state_controller = state_controller
        self.state_controller_address = state_controller_address
        self.actuator_controller = actuator_controller
        self.actuator_controller_address = actuator_controller_address


class Station:
    """Station which contains all bays, controller and card readers."""

    def __init__(self, config: StationConfig):
        """Initialize station from station config."""

        assert len({c.controller_id for c in config.state_controllers}) == len(config.state_controllers), \
            "Duplicate state controller ids in config"
        assert len({c.controller_id for c in config.actuator_controllers}) == len(config.actuator_controllers), \
            "Duplicate actuator controller ids in config"
        assert len({c[0] for c in config.bays}) == len(config.bays), "Duplicate bay ids in config"

        self.state_controllers: Dict[str, StateController] = {
            state_controller_config.controller_id: StateController(state_controller_config)
            for state_controller_config in config.state_controllers
        }
        self.actuator_controllers: Dict[str, ActuatorController] = {
            actuator_controller_config.controller_id: ActuatorController(actuator_controller_config)
            for actuator_controller_config in config.actuator_controllers
        }
        self.bays: Dict[str, Bay] = {
            bay_config[0]: Bay(
                bay_id=bay_config[0],
                state_controller=self.state_controllers[bay_config[1]],
                state_controller_address=Address(controller_register=bay_config[2], register_bit_mask=bay_config[3]),
                actuator_controller=self.actuator_controllers[bay_config[4]],
                actuator_controller_address=Address(controller_register=bay_config[5], register_bit_mask=bay_config[6]),
            )
            for bay_config in config.bays
        }

    def configure(self):
        """ Initialize all the ports. """

        for state_controller in self.state_controllers.values():
            state_controller.configure()
        for actuator_controller in self.actuator_controllers.values():
            actuator_controller.configure()

    def open_bay(self, bay_id: str) -> None:
        """Open the bay with the given id."""

        bay = self.bays[bay_id]
        bay.actuator_controller.open_bay(bay.actuator_controller_address)

    def open_all_bays(self) -> None:
        """Open all bays."""

        for bay in self.bays.values():
            bay.actuator_controller.open_bay(bay.actuator_controller_address)

    def get_states(self) -> Dict[str, bool]:
        """Gets the state of all bays."""

        return {
            bay.bay_id: bay.state_controller.is_open(bay.state_controller_address)
            for bay in self.bays.values()
        }

    def get_state(self, bay_id: str) -> bool:
        """Get the state of the bay with the given id."""

        bay = self.bays[bay_id]
        return bay.state_controller.is_open(bay.state_controller_address)
