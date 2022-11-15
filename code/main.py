import mesa as ms
import matplotlib.pyplot as plt

class TrashAgentModel(ms.Agent):
	def __init__(self, id_t, model):
		super().__init__(id_t, model)
		self.id = id_t

class VaccumAgentModel(ms.Agent):
	myCoordinates = (0, 0)
	def __init__(self, id_t, model):
		super().__init__(id_t, model)
		self.id = id_t

	def move(self):
		next_move = self.model.grid.get_neighborhood(
			self.pos, moore = True, include_center = False
		)
		new_position = self.random.choice(next_move)
		self.model.grid.move_agent(self, new_position)
	
	def step(self):
		self.move()
		x, y = self.pos
		this_cell = self.model.grid.get_cell_list_contents([self.pos])
		trash = [obj for obj in this_cell if isinstance(obj, TrashAgentModel)]
		if len(trash) > 0:
			trashToConseme = self.random.choice(trash)
			self.model.grid.remove_agent(trashToConseme)

class RoomModel(ms.Model):
	def __init__(self, n_agentsVacuum, n_agentsTrash):
		super().__init__()
		self.gobalTrash = n_agentsTrash
		self.gobalSteps = 1
		self.schedule = ms.time.RandomActivation(self)
		self.grid = ms.space.MultiGrid(10, 10, torus=False)
		for i in range(n_agentsVacuum):
			vac = VaccumAgentModel(i, self)
			self.schedule.add(vac)
			coordinates = (1, 1)
			vac.myCoordinates = coordinates
			self.grid.place_agent(vac, coordinates)

		for i in range(n_agentsTrash):
			trashAgent = TrashAgentModel(i, self)
			coordinates = (self.random.randrange(0, 10), self.random.randrange(0, 10))
			self.grid.place_agent(trashAgent, coordinates)

		self.datacollector_currents = ms.DataCollector(
			{
				"Wealthy Agents": RoomModel.current_weathy_agents,
				"Non Wealthy Agents": RoomModel.current_non_weathy_agents,
			}
		) 

	@staticmethod
	def current_weathy_agents(model) -> int:
		"""Return the total of number of weathy agents
		
		Args:
			model (RoomModel): tee simulation model
			
		Returns:
			int: Num of wealthy agents"""

		return sum([1 for agent in model.schedule.agents if agent.id > 0])

	@staticmethod
	def current_non_weathy_agents(model) -> int:
		"""Return the total of number of weathy agents
		
		Args:
			model (RoomModel): tee simulation model
			
		Returns:
			int: Num of wealthy agents"""


		return sum([1 for agent in model.schedule.agents if agent.id == 0])

	def step(self):
		if (self.gobalSteps == 151):
			
			return
		else:
			self.datacollector_currents.collect(self)
			self.gobalSteps += 1
			self.schedule.step()

model = RoomModel(5, 10)
model.step()

def agent_PT(agent):
    if type(agent) == VaccumAgentModel:
        PT = {
				"Shape": "circle",
				"Color": "blue",
				"Filled": "true",
				"Layer": 0,
				"r": 0.5,
		}
    else:
        PT = {
				"Shape": "circle",
				"Color": "gray",
				"Filled": "true",
				"Layer": 0,
				"r": 0.5,
		}
    return PT

grid = ms.visualization.CanvasGrid(agent_PT, 10, 10, 500, 500)

chart_currents = ms.visualization.ChartModule(
	[
		{"Label": "Wealthy Agents", "Color": "green"},
		{"Label":"Non Wealthy Agents", "Color": "red"},
	],
	canvas_height=300,
	data_collector_name="datacollector_currents"
)

server = ms.visualization.ModularServer(RoomModel, [grid, chart_currents], "Vacuum Room Model", {"n_agentsVacuum": 5, "n_agentsTrash": 35})
server.port = 8521
server.launch()

