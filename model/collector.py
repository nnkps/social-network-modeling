
def compute_avg_number_of_comments(model):
	comments_numbers = [len(agent.comments) for agent in model.schedule.agents]
	return sum(comments_numbers) / len(model.schedule.agents)