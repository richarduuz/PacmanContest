# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'MCTSAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

  def isTerminal(self, gameState):
    foodLeft=len(self.getFood(gameState).asList())
    if foodLeft<=2:
      return True
    else:
      return False

  def getSuccessor(self, gameState, action):
    successor=gameState.generateSuccessor(self.index, action)
    pos=successor.getAgentState(self.index).getPosition()
    if pos != util.nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):

    return


class MCTSAgent(DummyAgent):

  def __init__(self, index):
    super(DummyAgent, self).__init__(index)
    self.stateValue = util.Counter()
    self.visitTime = util.Counter()
    self.discount = 0.9
    self.epoch = 10
    self.beginActions = []


  def foodHeuristic(self, gameState):
    min = -10000
    currentActions = gameState.getLegalActions(self.index)
    myPos = gameState.getAgentState(self.index).getPosition()
    for action in currentActions:
      successor = self.getSuccessor(gameState, action)
      dis = self.getMazeDistance(myPos, successor.getAgentState(self.index).getPosition())
      if (dis > min):
        min = dis
    return min

  def isFoodTerminal(self, gameState):
    foodList = self.getFood(gameState).asList()
    if len(foodList) == 19:
      return True
    else:
      return False


  def wAstarSearch(self, gameState):
    myPos = gameState.getAgentState(self.index).getPosition()
    actions = []

    from util import PriorityQueue
    open = PriorityQueue()
    closed = {}
    closed[gameState] = 999999


    open.push((gameState, [], 0), 0 + self.foodHeuristic(gameState))
    while not open.isEmpty():
      gameState, actions, cost = open.pop()
      if gameState not in closed.keys() or closed[gameState] > cost + self.foodHeuristic(gameState):
        closed[gameState] = cost + self.foodHeuristic(gameState)
        if self.isFoodTerminal(gameState):
          return actions
        else:
          currentActions = gameState.getLegalActions(self.index)
          for action in currentActions:
            successor = self.getSuccessor(gameState, action)
            open.update((successor, actions+[action], cost+1), cost+1+self.foodHeuristic(successor))



  def chooseAction(self, gameState):
    if not gameState.getAgentState(self.index).isPacman:
      self.mctsProcess(gameState)
      if self.beginActions == []:
        self.beginActions = self.wAstarSearch(gameState)
      action = self.beginActions[0]
      temp = self.beginActions.pop(0)
      return action
    self.beginActions = []
    self.mctsProcess(gameState)
    actions = gameState.getLegalActions(self.index)
    max = -100000
    myPos = gameState.getAgentState(self.index).getPosition()
    if (myPos==(3,13)):
      print()
    bestAction = actions[0]
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      if (self.stateValue[successor] > max):
        max = self.stateValue[successor]
        bestAction = action
    self.stateValue[self.getSuccessor(gameState, bestAction)] -= 1
    return bestAction



  def mctsProcess(self, gameState):
    import math
    stack = util.Stack()
    rootState = gameState
    if self.visitTime[gameState] == 0 or not self.fullExpanded(gameState):
      stack.push(gameState)
      nextState = self.selectState(gameState)
      myPos = nextState.getAgentState(self.index).getPosition()
      self.visitTime[gameState] += 1

    else:
      stack.push(gameState)
      while (self.fullExpanded(gameState)):
        self.visitTime[gameState] += 1
        actions = gameState.getLegalActions(self.index)
        successors = []
        for action in actions:
          successors.append(self.getSuccessor(gameState, action))
        maxValue = -10000
        for successor in successors:
          ucbValue = self.stateValue[successor]/self.visitTime[successor] \
                   + math.sqrt(2 * math.log2(self.visitTime[gameState])/self.visitTime[successor])
          if ucbValue > maxValue:
            nextState = successor
        gameState = nextState
        stack.push(nextState)
      nextState = self.selectState(gameState)

    self.visitTime[gameState] += 1
    stack.push(nextState)
    currentScore = self.getScore(rootState)
    self.simulation(nextState, currentScore)
    self.visitTime[nextState] += 1
    self.backProcess(stack)



  def simulation(self, gameState, currentScore):
    import math

    foodList = self.getFood(gameState).asList()
    dis = 10000
    myPos = gameState.getAgentState(self.index).getPosition()

    for food in foodList:
      if dis > self.getMazeDistance(myPos, food):
        dis = self.getMazeDistance(myPos, food)
    #   dis += self.getMazeDistance(myPos, food)
    # dis = dis/len(foodList)
    reward = math.pow(self.discount, dis) * 50
    ghostReward = 0
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    if gameState.getAgentState(self.index).isPacman:
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        ghostDistance = min(dists)
        ghostReward = math.pow(ghostDistance, 250)



    score = self.getScore(gameState);
    self.stateValue[gameState] = reward - ghostReward + 50 * (score - currentScore)


  def backProcess(self, stack):
    preState = stack.pop()
    while not stack.isEmpty():
      state = stack.pop()
      self.stateValue[state] = self.discount*self.stateValue[preState]
      preState = state



  def valueIteration(self, gameState):
    state = gameState

  def fullExpanded(self, gameState):
    actions = gameState.getLegalActions(self.index)
    successors = []
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      if self.visitTime[successor] == 0:
        return False;
    return True

  def selectState(self, gameState):

    actions = gameState.getLegalActions(self.index)
    for action in actions:
      if self.visitTime[self.getSuccessor(gameState, action)] == 0:
        return self.getSuccessor(gameState, action)





class MDPAgent(DummyAgent):
  def __init__(self, index):
    super(DummyAgent, self).__init__(index)
    self.stateValue=util.Counter()
    self.discount=0.9
    # self.startState=gameState
    # self.valueIteration()

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    self.valueIteration(gameState)
    maxValue=0
    bestAction=''
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      currentValue = self.stateValue[successor]
      if currentValue>maxValue:
        maxValue=currentValue
        bestAction=action

    return bestAction
    # successors = [{[self.getSuccessor(gameState, action)]:action} for action in actions]


  def valueIteration(self, gameState):
    state=gameState
    foodLeft=len(self.getFood(gameState).asList())
    if foodLeft<20:
      return
    if self.isTerminal(state):
      return
    currentScore=self.getScore(state)
    # while not self.isTerminal(state):
    actions=state.getLegalActions(self.index)
    successors=[self.getSuccessor(state,action) for action in actions]
    maxValue=-10000
    currentValue = maxValue
    for successor in successors:
      myPos=successor.getAgentState(self.index).getPosition()
      if not (self.isTerminal(state)):
        enemies=[successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghosts=[a for a in enemies if a.isPacman and a.getPosition()!=None]
        ghostReward=0
        if len(ghosts)>0:
          dists = [self.getMazeDistance(myPos,a.getPosition()) for a in ghosts]
          ghostDistance = min(dists)
          ghostReward=1/ghostDistance*250
        if myPos in self.getFood(successor).asList():
          currentValue=10-1+self.discount*self.stateValue[successor]+ghostReward
        elif not successor.getAgentState(self.index).isPacman:
          futureScofe=self.getScore(successor)
          if self.red:
             currentValue=futureScofe-currentScore-1+self.discount*self.stateValue[successor]+ghostReward
          else:
            currentValue=currentScore-futureScofe-1+self.discount*self.stateValue[successor]+ghostReward
      else:
        currentValue=10000
      if currentValue > maxValue:
        maxValue = currentValue
          # TODO add some other situations
      self.stateValue[state]=maxValue
    for successor in successors:
      self.valueIteration(successor)

