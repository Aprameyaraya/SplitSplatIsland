"""Regions 1-3: The Basics, Extensive Form Games, Advanced Strategic Form Games."""
from sp_engine import *

SG = [[(3, 3), (0, 5)], [(5, 0), (1, 1)]]
SR = ["Share", "Grab"]
STAG = [[(4, 4), (0, 3)], [(3, 0), (3, 3)]]
STR = ["Stag", "Hare"]
RIG = [[(2, -2), (-1, 1)], [(-1, 1), (1, -1)]]
HT = ["Heads", "Tails"]
BOS = [[(2, 1), (0, 0)], [(0, 0), (1, 2)]]
OF = ["Opera", "Football"]
IES = [[(1, 1), (3, 2), (2, 1)], [(3, 2), (2, 3), (0, 1)], [(1, 4), (0, 2), (4, 0)]]
MD = [[(3, 2), (0, 1)], [(0, 1), (3, 2)], [(1, 1), (1, 1)]]
WEAK = [[(2, 1), (0, 0)], [(2, 0), (1, 1)]]
PD2 = [[(3, 3), (0, 4)], [(4, 0), (1, 1)]]
ST2 = [[(3, 3), (0, 0)], [(0, 0), (1, 1)]]
RPS = [[(0, 0), (-1, 1), (1, -1)], [(1, -1), (0, 0), (-1, 1)], [(-1, 1), (1, -1), (0, 0)]]
RPSN = ["Rock", "Paper", "Scissors"]
MRPS = [[(0, 0), (-1, 1), (2, -2)], [(1, -1), (0, 0), (-1, 1)], [(-2, 2), (1, -1), (0, 0)]]
PEN = [[(5, 5), (7, 3)], [(9, 1), (6, 4)]]
PEN2 = [[(5, 7), (7, 3)], [(9, 1), (6, 4)]]
PR, PC = ["Kick Left", "Kick Right"], ["Dive Left", "Dive Right"]
STAGE2 = [[(3, 1), (1, 0)], [(2, 1), (0, 2)]]
UD, LR = ["Up", "Down"], ["Left", "Right"]

REGION1 = [
    lvl("Strict Dominance", "Gus the Gull", "shore",
        [("N", "Your ship splits on the rocks. You wash up on SPLITSPLAT ISLAND, where every creature plays games and nobody leaves until they can out-think the island's champions."),
         ("E", "Squawk! I'm Gus. We play Coconut Grab: each round we secretly pick SHARE or GRAB. BLUE numbers are yours, RED are mine."),
         ("Y", "If we both Share we get 3 each, but if I Grab while he Shares I get 5...")],
        [lambda: MatrixPlay(dict(title="Level 1 - Coconut Grab with Gus", theme="shore", short="Gus", rows=SR, cols=SR, pay=SG, rounds=5, enemy=e_always(1),
                                 goal=GOAL_TIE.format("Gus"), tip="Think: what is best for you NO MATTER what Gus does? (Try the best-replies toggle.)"))],
        "LESSON - STRICT DOMINANCE: a strategy strictly dominates another if it pays more NO MATTER what the opponent does. Rational players never play strictly dominated strategies. In the Prisoner's Dilemma, Grab strictly dominates Share, so both Grab and both end up worse off than if they had shared.",
        [Q("Which of YOUR strategies is strictly dominant?", ["Share, whatever Gus decides to do", "Grab, whatever Gus decides to do", "Neither, it depends on Gus's choice", "Both, since each can win sometimes"], 1,
           "Grab beats Share against Share (5 vs 3) AND against Grab (1 vs 0).", "Compare your blue payoffs column by column. Which option wins in both columns?"),
         Q("Both players use their dominant strategy. What outcome results?", ["Both players earn 3 points each", "Both players earn 1 point each", "You earn 5 and Gus earns 0", "You earn 0 and Gus earns 5"], 1,
           "Prisoner's Dilemma: individually rational choices leave both worse off than (Share, Share).", "What does Gus do if he also follows his dominant strategy?")],
        matrix_extra(SG, SR, SR)),

    lvl("Eliminating", "Penny the Pelican", "shore",
        [("E", "Pelican Post! I never deliver to strategies that someone else clearly beats. This 3x3 table is a mess. Delete the losers, one at a time.")],
        [lambda: Eliminate(dict(title="Level 2 - Iterated Elimination", theme="shore", rows=["Top", "Middle", "Bottom"], cols=["Left", "Center", "Right"], pay=IES,
                                tip="Click the NAME of a strictly dominated strategy to delete it. Deleting can create NEW dominated strategies, so re-check after each step.",
                                stuck="Only one outcome survives."))],
        "LESSON - ITERATED ELIMINATION OF STRICTLY DOMINATED STRATEGIES: delete a strictly dominated strategy, then look at the smaller game: new strategies may now be dominated. Repeat. If one cell survives, it is the Nash equilibrium. For strict dominance the order of deletion does not change the result.",
        [Q("Which strategy can be deleted FIRST?", ["Left", "Center", "Right", "Bottom"], 2, "Center beats Right for the column player in every row (2>1, 3>1, 2>0).", "Check each strategy: is it worse than another in EVERY row/column? Only one passes at the start."),
         Q("Which outcome survives iterated elimination?", ["Top and Center together", "Middle and Center together", "Top and Left together", "Bottom and Right together"], 0, "Right, then Bottom, then Left, then Middle go: (Top, Center) remains.", "Delete in order: Right, Bottom, Left, Middle."),
         Q("Does the deletion order change the final result under STRICT dominance?", ["No, the survivor is identical", "Yes, the survivor can differ", "Only with three strategies", "Only with negative payoffs"], 0, "Strictly dominated strategies are never part of an equilibrium, so any order ends in the same place.", "Strict dominance never throws away an equilibrium.")],
        matrix_extra(IES, ["Top", "Middle", "Bottom"], ["Left", "Center", "Right"])),

    lvl("Nash & Stag Hunt", "Tess the Turtle", "shore",
        [("E", "Slow and steady... We hunt together. Stag pays 4 each if BOTH hunt Stag; alone on the Stag you get nothing. Hare is a safe 3. I always chase the Hare, it's tradition.")],
        [lambda: MatrixPlay(dict(title="Level 3 - Stag Hunt with Tess", theme="shore", short="Tess", rows=STR, cols=STR, pay=STAG, rounds=5, enemy=e_always(1),
                                 goal=GOAL_TIE.format("Tess"), tip="Find your BEST RESPONSE to what Tess does. Then find the Nash equilibria.")),
         lambda: NashPicker(dict(title="Level 3 - Find the Nash equilibria", theme="shore", rows=STR, cols=STR, pay=STAG))],
        ["LESSON - BEST RESPONSES AND NASH EQUILIBRIUM: a best response is the action that pays you most given what the other player does. A pure-strategy Nash equilibrium is a cell where EVERY player is best-responding at once, so nobody gains by switching alone. Tip: underline each player's best payoffs; cells with both underlined are Nash.",
         "Stag Hunt has two pure equilibria, (Stag, Stag) and (Hare, Hare), and neither player has a dominant strategy."],
        [Q("Tess plays Stag. What is your best response?", ["Hunt the Stag as well", "Chase the Hare instead", "Either one, they pay the same", "Stay home and do nothing"], 0, "Against Stag: Stag pays 4, Hare pays 3.", "Look at the Stag column and compare your two blue payoffs."),
         Q("Does either player have a strictly dominant strategy here?", ["Yes, Stag dominates Hare", "Yes, Hare dominates Stag", "No, neither one dominates", "Yes, both dominate each other"], 2, "Stag is best against Stag, Hare is best against Hare, so no strategy dominates.", "Check whether one action is better in BOTH columns.")],
        matrix_extra(STAG, STR, STR)),

    lvl("Mixed Strategies", "Clara the Crab", "shore",
        [("E", "Click clack! Pebble Toss. We each hide a pebble, Heads or Tails up. If they MATCH you win, if they DIFFER I win. Any habit you show, I exploit."),
         ("Y", "So I need to randomize, and I need to CALCULATE the right odds.")],
        [lambda: Calc("shore", "Level 4 - Mixed Strategy Algorithm", [
            dict(prompt="Clara rigged the pebbles! Matching on Heads pays you +2, matching on Tails +1, any mismatch costs you 1. Let p = your chance of Heads. Choose p so that CLARA is indifferent.",
                 matrix=(RIG, HT, HT), fields=[("p (your chance of Heads) =", 0.4)],
                 hints=["If Clara plays Heads, your EV = p(2) + (1-p)(-1) = 3p - 1", "If Clara plays Tails, your EV = p(-1) + (1-p)(1) = 1 - 2p", "Set equal: 3p - 1 = 1 - 2p, so 5p = 2 and p = 0.4"],
                 wrong=lambda v: f"At p = {fmt(round(v[0], 3))}: against Heads you get {3 * v[0] - 1:.2f}, against Tails {1 - 2 * v[0]:.2f}. They must be EQUAL.",
                 ok="Correct! p = 2/5. Now Clara's side: her mix comes from YOUR payoffs."),
            dict(prompt="Now let q = Clara's chance of Heads. Choose q so that YOU are indifferent between Heads and Tails. (Remember: your payoffs decide HER probabilities.)",
                 matrix=(RIG, HT, HT), fields=[("q (Clara's chance of Heads) =", 0.4)],
                 hints=["If you play Heads, your EV = q(2) + (1-q)(-1) = 3q - 1", "If you play Tails, your EV = q(-1) + (1-q)(1) = 1 - 2q", "Equal: 5q = 2, so q = 0.4"],
                 wrong=lambda v: f"At q = {fmt(round(v[0], 3))}: Heads earns you {3 * v[0] - 1:.2f}, Tails earns you {1 - 2 * v[0]:.2f}. They must be EQUAL.",
                 ok="Correct! Equilibrium: (Heads 2/5, Tails 3/5 ; Heads 2/5, Tails 3/5). Throw pebbles until you are at a win or tie.", throw=(RIG, 0.4, 0.4))],
            pages=[("Clara exploits any pattern. So choose a PROBABILITY instead. The trick: pick your probability so the OTHER player gets the SAME expected payoff from either of her actions. Then nothing she does can beat you.", None),
                   ("Matching Pennies: you win +1 on a match, -1 on a mismatch. Let p = your chance of Heads.\nIf Clara shows Heads: p(+1) + (1-p)(-1) = 2p - 1.\nIf Clara shows Tails: p(-1) + (1-p)(+1) = 1 - 2p.", ([[(1, -1), (-1, 1)], [(-1, 1), (1, -1)]], HT, HT)),
                   ("Make them equal: 2p - 1 = 1 - 2p, so 4p = 2 and p = 1/2.\nThat is the mixed Nash equilibrium of Matching Pennies.", ([[(1, -1), (-1, 1)], [(-1, 1), (1, -1)]], HT, HT)),
                   ("THE MIXED STRATEGY ALGORITHM\n1) Let p be a player's chance of the first action.\n2) Write the OTHER player's expected payoff for each of her actions.\n3) Set them equal.\n4) Solve for p. Repeat for the other player.\n\nHOW NOT TO WRITE IT: do not give one number. State BOTH players' full mixtures, like (Heads 1/2, Tails 1/2 ; Heads 1/2, Tails 1/2).", None)])],
        "LESSON - MIXED STRATEGY NASH EQUILIBRIUM: when no pure equilibrium exists, players randomize. Your probabilities are chosen to make the OTHER player indifferent, so they come from the other player's payoffs. A full answer lists every player's mixture.",
        [Q("Which is a correct way to write a mixed strategy Nash equilibrium?", ["(2/5 Heads, 3/5 Tails ; 2/5 Heads, 3/5 Tails)", "Both players simply play Heads and Tails", "The single probability p equals two fifths", "Heads for you and Tails for Clara"], 0, "A mixed equilibrium states each player's complete probability distribution.", "The answer must describe BOTH players and ALL of their actions."),
         Q("A player's equilibrium mix is chosen so that...", ['her opponent becomes indifferent', 'her own expected payoff is maximized', 'all of the cells are equally likely', 'she avoids all weak strategies'], 0, "Mixing at the right odds makes the opponent's expected payoff identical either way, so she cannot gain by switching.", "Recall step 2 of the algorithm.")]),

    lvl("Battle of the Sexes", "Pete the Parrot", "shore",
        [("E", "Prrrk! Opera or Football? You prefer Opera, I prefer Football, but we both want to go TOGETHER. Meet and you each score; miss and you get nothing.")],
        [lambda: NashPicker(dict(title="Level 5 - Battle of the Sexes", theme="shore", rows=OF, cols=OF, pay=BOS, ok="Correct! Two pure equilibria... and there is a third, mixed one hiding.")),
         lambda: Calc("shore", "Level 5 - Mixed equilibrium and payoffs", [
             dict(prompt="Find the mixed equilibrium. p = chance the ROW player picks Opera (makes the column player indifferent). q = chance the COLUMN player picks Opera (makes the row player indifferent).",
                  matrix=(BOS, OF, OF), fields=[("p (row plays Opera) =", 2 / 3), ("q (column plays Opera) =", 1 / 3)],
                  hints=["Column's EV: Opera = p(1) + (1-p)(0) = p ; Football = p(0) + (1-p)(2) = 2 - 2p", "Row's EV: Opera = q(2) = 2q ; Football = (1-q)(1) = 1 - q", "p = 2 - 2p gives p = 2/3.  2q = 1 - q gives q = 1/3."],
                  wrong=lambda v: f"Column gets {v[0]:.2f} from Opera vs {2 * (1 - v[0]):.2f} from Football. Row gets {2 * v[1]:.2f} from Opera vs {1 - v[1]:.2f} from Football. Each pair must be EQUAL.",
                  ok="Correct! Mixed equilibrium: (Opera 2/3, Football 1/3 ; Opera 1/3, Football 2/3)."),
             dict(prompt="Now calculate each player's expected payoff in that mixed equilibrium.",
                  matrix=(BOS, OF, OF), fields=[("Row player's payoff =", 2 / 3), ("Column player's payoff =", 2 / 3)],
                  hints=["Cell probabilities: (O,O) = 2/3 x 1/3 = 2/9, (F,F) = 1/3 x 2/3 = 2/9, off-diagonals are 4/9 and 1/9", "Row: 2(2/9) + 1(2/9) + 0 + 0 = 6/9", "Column: 1(2/9) + 2(2/9) = 6/9. Both get 2/3."],
                  ok="Correct! Both get 2/3, worse than either pure equilibrium (they sometimes miss each other).")],
             pages=[("Pure equilibria are not the end of the story. Battle of the Sexes also has a MIXED equilibrium, found with the same indifference trick.", (BOS, OF, OF)),
                    ("CALCULATING PAYOFFS\n1) Write each player's probabilities next to the strategies.\n2) Multiply the two probabilities in each cell.\n3) Multiply each cell's probability by a player's payoff there.\n4) Add them up: that is the expected payoff.", (BOS, OF, OF))])],
        "LESSON - BATTLE OF THE SEXES: two pure-strategy equilibria (both Opera, both Football) plus one mixed equilibrium. To find expected payoffs in a mixed equilibrium, multiply cell probabilities by payoffs and sum.",
        [Q("How many Nash equilibria does this game have (pure plus mixed)?", ["Exactly one", "Exactly two", "Exactly three", "Exactly four"], 2, "Two pure plus one mixed makes three.", "Count the pure cells you found, then add the mixed one."),
         Q("Where does a player's equilibrium mix come from?", ["The opponent's payoffs, to make her indifferent", 'Her own payoffs, to maximize her earnings', 'The matrix size, with everything split evenly', 'A fair coin that is used in every game'], 0, "Each player's probabilities are set from the OTHER player's payoffs.", "Which payoffs did you use to find p?")]),

    lvl("Mixed Dominance", "Penny the Pelican", "shore",
        [("E", "Pelican Post, part two! Here no single strategy beats Middle... but a MIX of two others might. Can you spot it?")],
        [lambda: Eliminate(dict(title="Level 6 - Strict Dominance by a Mixture", theme="shore", rows=["Up", "Down", "Middle"], cols=LR, pay=MD, mixed=True,
                                tip="No pure strategy dominates anything here. Click Middle: it may be dominated by a MIXTURE of two other strategies.",
                                stuck="No strictly dominated strategies remain, so the game continues with mixed strategies."))],
        "LESSON - STRICT DOMINANCE IN MIXED STRATEGIES: if a mixture of two strategies strictly dominates a third, you may eliminate the third. Then continue iterated elimination as usual.",
        [Q("Middle pays 1 in both columns. Which mixture strictly beats it?", ["Up 50 percent and Down 50 percent", "Up 20 percent and Down 80 percent", "Up 100 percent and Down 0 percent", "Down 100 percent and Up 0 percent"], 0, "The 50/50 mix earns 1.5 against either column, more than 1.", "Compute the mixture's payoff in BOTH columns."),
         Q("After deleting Middle, is any other strategy strictly dominated?", ["No, none remain dominated", "Yes, Left dominates Right", "Yes, Up dominates Down", "Yes, Right dominates Left"], 0, "Up and Down each win one column, and Left and Right each win one row.", "Check both players' strategies in the smaller game.")],
        matrix_extra(MD, ["Up", "Down", "Middle"], LR)),

    lvl("Weak Dominance", "Pete the Parrot", "shore",
        [("E", "Prrrk! Top and Bottom tie against my Left perch, but Bottom wins against my Right. Is Top worth keeping?")],
        [lambda: Eliminate(dict(title="Level 7 - Weak Dominance", theme="shore", rows=["Top", "Bottom"], cols=LR, pay=WEAK, weak=True,
                                tip="Weak dominance: never better, sometimes worse. Delete weakly dominated strategies and see where you end up.",
                                stuck="Elimination finished.")),
         lambda: NashPicker(dict(title="Level 7 - But what are the real equilibria?", theme="shore", rows=["Top", "Bottom"], cols=LR, pay=WEAK,
                                 ok="Correct! Elimination found only (Bottom, Right), but (Top, Left) is Nash too. Deleting weakly dominated strategies lost an equilibrium."))],
        ["LESSON - WEAK DOMINANCE: a strategy is weakly dominated if another is never worse and sometimes strictly better. Unlike strict dominance, deleting weakly dominated strategies can throw away real Nash equilibria.",
         "INFINITELY MANY EQUILIBRIA: against Left, Top and Bottom tie, so the row player may mix them in ANY proportion (as long as the column player still prefers Left). Some games have a whole RANGE of mixed equilibria, and a full solution must state that range."],
        [Q("How many Nash equilibria does this game have?", ["Exactly two", "Exactly three", "Infinitely many", "Exactly one"], 2, "(Bottom, Right), plus any mixture of Top and Bottom for the row player (with enough Top) against Left.", "The row player is indifferent between Top and Bottom against Left."),
         Q("What is the danger of deleting weakly dominated strategies?", ["You may delete real equilibria", "You may create fake equilibria", "You change every payoff", "Nothing, it is always safe"], 0, "Any equilibrium you keep is still real, but you can miss some.", "Which equilibrium did elimination miss?")],
        matrix_extra(WEAK, ["Top", "Bottom"], LR)),

    lvl("The Odd Rule", "Gus the Gull", "shore",
        [("E", "Squawk! Last test on the coast: counting. How many equilibria should a game have? Careful, mixed ones count too.")],
        [lambda: Calc("shore", "Level 8 - Count the Equilibria", [
            dict(prompt="Stag Hunt. Its pure equilibria are (Stag, Stag) and (Hare, Hare). Use the odd rule: how many equilibria are there in TOTAL, pure and mixed?", matrix=(STAG, STR, STR),
                 fields=[("Total equilibria =", 3)], hints=["Two pure equilibria is an even number", "The odd rule says an odd total is normal, so one mixed equilibrium is hiding", "Total = 3"], ok="Correct: 3 (the mixed one has Stag 3/4 of the time)."),
            dict(prompt="Prisoner's Dilemma. How many equilibria are there in total?", matrix=(SG, SR, SR),
                 fields=[("Total equilibria =", 1)], hints=["Does either player have a strictly dominant strategy?", "Grab strictly dominates Share, so only (Grab, Grab) survives and no mixing is possible"], ok="Correct: just 1."),
            dict(prompt="Battle of the Sexes. Two pure equilibria (Opera, Opera) and (Football, Football). How many in total?", matrix=(BOS, OF, OF),
                 fields=[("Total equilibria =", 3)], hints=["Two pure equilibria again, which is even", "There is a mixed equilibrium too (you computed it earlier)"], ok="Correct: 3.")])],
        "LESSON - THE ODD RULE: most games have an ODD number of equilibria (pure and mixed together). Games with an even number, or infinitely many, tend to feature a lot of weak dominance. If you counted an even number, you probably missed a mixed equilibrium.",
        [Q("How many Nash equilibria (pure and mixed) does the Stag Hunt have?", ["One", "Two", "Three", "Four"], 2, "(Stag, Stag), (Hare, Hare), plus a mixed one with Stag 3/4 of the time.", "Two pure ones... and the odd rule says the total should be odd."),
         Q("How many Nash equilibria does the Prisoner's Dilemma have?", ["One", "Two", "Three", "Four"], 0, "Only (Grab, Grab), and one is odd. Strict dominance leaves no room for mixing.", "Delete the strictly dominated strategies first."),
         Q("You carefully find exactly two equilibria. What does the odd rule suggest?", ["You missed one, or weak dominance exists", "The game must be zero-sum entirely", "Both equilibria are secretly fake ones", "Nash equilibria always come in pairs"], 0, "Even counts usually mean a missed mixed equilibrium or weak dominance.", "Which counts are 'normal' for most games?")],
        matrix_extra(STAG, STR, STR)),
]

TREE_CAVE = lambda: N("A", 0, [("Stay out", (0, 3)), ("Enter", N("B", 1, [("Fight", (-1, 0)), ("Share", (2, 1))]))])
TREE_WRITE = lambda: N("A", 0, [("Left", N("B", 1, [("Up", (3, 2)), ("Down", (0, 0))])), ("Right", N("C", 1, [("Up", (1, 3)), ("Down", (2, 1))]))])
TREE_MULTI = lambda: N("A", 0, [("Out", (1, 1)), ("In", N("B", 1, [("X", (3, 2)), ("Y", (0, 2))]))])
TREE_BURN = lambda: N("A", 0, [("Burn bridge", N("B", 1, [("Give in", (3, 0)), ("Resist", (-1, -2))])),
                               ("Keep bridge", N("C", 1, [("Give in", (3, 0)), ("Resist", N("D", 0, [("Fight", (-1, -2)), ("Retreat", (0, 1))]))]))])
TREE_CENT = lambda: N("A", 0, [("Take", (1, 0)), ("Pass", N("B", 1, [("Take", (0, 2)), ("Pass", N("C", 0, [("Take", (3, 1)), ("Pass", N("D", 1, [("Take", (2, 4)), ("Pass", (4, 3))]))]))]))])

REGION2 = [
    lvl("Backward Induction", "Fenwick the Fox", "bridges",
        [("E", "Behold my treasure cave! Stay out and I keep it all (you get 0, I get 3). But if you ENTER, I'll FIGHT you! Don't test me."),
         ("N", "This game is SEQUENTIAL: you move, then Fox sees it and moves. A tree shows it. Each decision point whose future can be analyzed on its own starts a SUBGAME.")],
        [lambda: Tree(dict(title="Level 8 - Backward Induction", theme="bridges", names=["You", "Fox"], tree=TREE_CAVE,
                           prompt="Solve from the BOTTOM: first Fox's node B, then your node A. At each node, pick the action that pays the mover most, given the choices already solved below."))],
        "LESSON - SUBGAME PERFECT EQUILIBRIUM AND BACKWARD INDUCTION: an SPE is a strategy profile that is a Nash equilibrium in EVERY subgame. Find it by BACKWARD INDUCTION: solve the last decisions first, then work back to the root. Threats that would not be carried out when the time comes are not credible.",
        [Q("Suppose you enter. What will Fox choose at his node?", ["He will share the treasure", "He will fight you as promised", "He will flee the cave at once", "He will choose at random"], 0, "Share pays Fox 1, Fight pays 0, so Fox shares.", "Compare Fox's red payoffs at his two leaves."),
         Q("Which strategy profile is the subgame perfect equilibrium?", ["You enter and Fox shares", "You stay out and Fox fights", "You enter and Fox fights", "You stay out and Fox shares"], 0, "Fox's threat is empty, so entering (2) beats staying out (0).", "Solve Fox's node first, then yours."),
         Q("Fox's fight threat is not credible because...", ['fighting is not his best reply there', 'foxes are poor liars in general', 'you cannot see his payoffs just yet', 'the treasure belongs to you already'], 0, "(Stay out, Fight) is a Nash equilibrium of the whole game but not subgame perfect: Fight is not optimal in Fox's subgame.", "What would a rational Fox do once you have really entered?")],
        tree_extra(TREE_CAVE, ["You", "Fox"])),

    lvl("Writing SPE", "Fenwick the Fox", "bridges",
        [("E", "Two more games. In the first, I make choices even in places the game will never reach. In the second, I do not care which of two options I take... and that matters.")],
        [lambda: Tree(dict(title="Level 9 - Complete the equilibrium", theme="bridges", names=["You", "Fox"], tree=TREE_WRITE,
                           prompt="Choose an action at EVERY decision node (A, B and C), even ones the equilibrium never reaches.")),
         lambda: Tree(dict(title="Level 9 - When someone is indifferent", theme="bridges", names=["You", "Fox"], tree=TREE_MULTI,
                           prompt="Fox is indifferent at node B (both of his options pay him 2). Solve it, then try again with the OTHER tie choice to see the second equilibrium."))],
        ["LESSON - HOW NOT TO WRITE AN SPE: an SPE must state a choice at EVERY decision node, including ones off the path of play. Writing only the path (Left, Up) is incomplete and wrong.",
         "MULTIPLE SPE: most games have one SPE, but when a player gets the SAME payoff from two actions they are indifferent and may pick either. Each tie can produce another equilibrium."],
        [Q("Which is a complete description of the SPE in the first game?", ['You Left; Fox Up at B and Up at C', 'You Left; Fox Up at B, nothing at C', 'Only the path: Left, then Up, then stop', 'Only the final payoffs, which are (3, 2)'], 0, "Fox must have a plan at C too, even though C is never reached.", "Count the decision nodes: every one needs an action."),
         Q("Why does the second game have two SPE?", ["Fox is indifferent between X and Y", "You are indifferent between In and Out", "Both players move at the same time", "The tree has exactly two leaves"], 0, "If Fox picks X you go In; if he picks Y you stay Out. Both are consistent.", "Look for equal payoffs for the mover at a node.")],
        tree_extra(TREE_WRITE, ["You", "Fox"])),

    lvl("Games w/ Stages", "Rusty the Raccoon", "bridges",
        [("E", "Two rounds, buddy. Stage 1 is Share/Grab, stage 2 is another game. You see what I did in stage 1. Payoffs just add up.")],
        [lambda: Calc("bridges", "Level 10 - Games with Stages", [
            dict(prompt="Backward induction: solve STAGE 2 first. Find its unique Nash equilibrium and enter each player's payoff there.",
                 matrix=(STAGE2, UD, LR), fields=[("Your stage-2 payoff =", 3), ("Rusty's stage-2 payoff =", 1)],
                 hints=["Underline best replies. Against Left you prefer Up (3 vs 2). Against Up, Rusty prefers Left (1 vs 0)", "(Up, Left) is the only cell where both are best-responding", "Payoffs: (3, 1)"],
                 ok="Correct: (Up, Left) with payoffs (3, 1)."),
            dict(prompt="Stage 1 is Share/Grab (shown). Whatever happens in stage 1, stage 2 adds (3, 1). Find the SPE of the whole game and enter the TOTAL payoffs.",
                 matrix=(SG, SR, SR), fields=[("Your total =", 4), ("Rusty's total =", 2)],
                 hints=["Adding the same (3, 1) to every cell does not change stage-1 incentives", "Grab still strictly dominates Share, so stage 1 is (Grab, Grab) = (1, 1)", "Total: (1+3, 1+1) = (4, 2)"],
                 ok="Correct! Totals (4, 2): Nash equilibrium in every stage.")],
            pages=[("A game has STAGES if it has multiple phases. Players see earlier moves, and payoffs from one stage do not directly change the next stage's payoffs. Solve by backward induction: the LAST stage first.", None)])],
        "LESSON - GAMES WITH STAGES: in the final stage, players must play a Nash equilibrium in every SPE. Playing a Nash equilibrium of the stage game in every stage is always an SPE. But there can be MORE equilibria (like cooperating in a Prisoner's Dilemma) if later stages can reward or punish.",
        [Q("In the last stage, what must players do in every SPE?", ['Play a Nash equilibrium of that stage', 'Cooperate with each other whenever possible', 'Mirror whatever they did in stage one', 'Mix uniformly over all of their strategies'], 0, "Nothing comes after the last stage, so only a stage Nash equilibrium is credible.", "Think of backward induction: what is the last subgame?"),
         Q("Is playing the stage Nash equilibrium in every stage an SPE?", ["Yes, it is always subgame perfect", "No, it is never subgame perfect", "Only when there are two stages", "Only when all payoffs are positive"], 0, "Each stage's play is a best reply, and later play does not depend on it.", "Check the one-stage deviations: does anyone gain?")]),

    lvl("Punishment", "Rusty the Raccoon", "bridges",
        [("E", "Stage 1 is Share/Grab. Stage 2 is a coordination game with TWO equilibria: (Good, Good) pays 3 each, (Bad, Bad) pays 1 each. Let's see if you can cooperate.")],
        [lambda: TwoStage(dict(title="Level 11 - Punishment Strategies", theme="bridges", short="Rusty", rows1=SR, cols1=SR, m1=PD2, rows2=["Good", "Bad"], cols2=["Good", "Bad"], m2=ST2,
                               e1=0, e2=lambda o: 0 if o == (0, 0) else 1, goal=6,
                               tip="Rusty Shares in stage 1. In stage 2 he plays Good if both of you Shared in stage 1, and Bad otherwise. Both stage-2 outcomes (Good,Good) and (Bad,Bad) are equilibria.",
                               goal_text="", ))],
        "LESSON - PUNISHMENT STRATEGIES: if stage 2 has multiple Nash equilibria, players can threaten to play the BAD one after a stage-1 deviation. The threat is credible because the bad outcome is still a Nash equilibrium. Here Grab gains 1 in stage 1 but loses 2 in stage 2, so cooperating in the Prisoner's Dilemma is part of an SPE.",
        [Q("What makes the (Bad, Bad) punishment credible?", ["It is a Nash equilibrium of stage two", "It costs the punisher nothing at all", "The punished player agrees to it", "It happens in the first stage"], 0, "Nobody can gain by deviating from it, so carrying out the threat is rational.", "Compare with Fox's empty threat: was his optimal?"),
         Q("Grabbing in stage 1 gains 1 but costs 2 later. So...", ["cooperating in stage 1 is sustainable", "Grabbing is always the best option", "stage 2 should be skipped entirely", "the punishment must be even larger"], 0, "The deviation is unprofitable, so (Share, Share) then (Good, Good) can be an SPE.", "Add up your total payoff from Grabbing versus Sharing."),
         Q("If stage 2 had only ONE Nash equilibrium, could the punishment work?", ['No, stage 2 play would be fixed', 'Yes, by using a mixed stage 1', 'Yes, as long as stage 1 is longer', 'Only if some payoffs are negative'], 0, "With one equilibrium there is no worse equilibrium to threaten.", "What would the 'punishment' stage-2 outcome be then?")]),

    lvl("Tying Hands", "Grizelda the Gorilla", "bridges",
        [("E", "GRRR. I command this army. Before the battle I can BURN my own retreat bridge. Why would anyone remove their own options? Let's solve it.")],
        [lambda: Tree(dict(title="Level 12 - Burning Bridges", theme="bridges", names=["General", "Rival"], tree=TREE_BURN,
                           prompt="Solve by backward induction. Node D: the General decides what to do if the Rival resists and the bridge is intact. Then C, B, A."))],
        ["LESSON - TYING HANDS (BURNING BRIDGES): sometimes having FEWER options helps. By destroying her own retreat, the General makes fighting her only option, so the Rival's resistance becomes costly and he gives in. Commitment is valuable because it makes threats credible.",
         "LESSON - COMMITMENT PROBLEMS: when one side expects to grow stronger, it cannot credibly promise to stay modest later. A declining rival may therefore prefer to fight NOW (preventive war) because no promise about the future is believable."],
        [Q("Why does burning the bridge help the General?", ["It makes fighting the only option left", "It adds a retreat option later", "It changes the Rival's payoffs directly", "It hides her payoffs from the Rival"], 0, "Without the retreat, Resist leads to a costly fight for the Rival, so he gives in.", "What would the General do at node D if she kept the bridge?"),
         Q("A rising power cannot promise to stay modest. What might a declining rival do?", ["Attack now, before the shift", "Wait quietly for the shift", "Offer the rising power more", "Disband its military fully"], 0, "The inability to commit can make war rational even when a bargain exists.", "Why is a promise about the future not believable?")],
        tree_extra(TREE_BURN, ["General", "Rival"])),

    lvl("Centipede", "Moe the Monkey", "bridges",
        [("E", "Ooh ooh! Banana pile! Each turn you can TAKE the pile or PASS it so it grows. Passing all the way gives both of us more... if we trust each other.")],
        [lambda: Tree(dict(title="Level 13 - The Centipede Game", theme="bridges", names=["You", "Moe"], tree=TREE_CENT,
                           prompt="Solve by backward induction from the last node D upward. At each node, is taking now better than passing to the next solved node?"))],
        ["LESSON - THE CENTIPEDE GAME: backward induction says the first mover Takes immediately (1, 0), even though passing to the end would give (4, 3). The solution looks bad, and real players often pass.",
         "LESSON - PROBLEMS WITH BACKWARD INDUCTION: it assumes all FUTURE play is rational, but if someone has already passed, rationality was already violated, so why trust it later? FORWARD INDUCTION flips this: it assumes all PAST play was rational and asks what a move reveals about the player."],
        [Q("What does backward induction predict at the first node?", ["Take immediately", "Pass, then take at the end", "Pass until the last node", "Randomize at every node"], 0, "At node D Moe takes, so C takes, so B takes, so A takes.", "Solve D first and work up."),
         Q("What is the main problem with backward induction?", ["It assumes all future play is rational", "It cannot analyze any game trees", "It always predicts mixed strategies", "It requires simultaneous moves"], 0, "If rationality has already failed, future rationality is questionable.", "What assumption do you make about players at later nodes?"),
         Q("How does forward induction differ?", ['It assumes all past play was rational', 'It assumes all future play is random', 'It ignores the payoffs of every player', 'It applies only to repeated games'], 0, "Forward induction reads past moves as meaningful signals of intent.", "Forward and backward point opposite ways in time.")],
        tree_extra(TREE_CENT, ["You", "Moe"])),
]

REGION3 = [
    lvl("Gen. Battle", "Clara the Crab", "tide",
        [("E", "Click clack! Battle of the Sexes again, but with different numbers. And this time I check that your answer is a REAL probability.")],
        [lambda: Calc("tide", "Level 14 - Generalized Battle of the Sexes", [
            dict(prompt="Find the mixed equilibrium. p = chance the ROW player picks Opera, q = chance the COLUMN player picks Opera.",
                 matrix=([[(4, 1), (0, 0)], [(0, 0), (2, 3)]], OF, OF), fields=[("p (row plays Opera) =", 0.75), ("q (column plays Opera) =", 1 / 3)],
                 hints=["Column's EV: Opera = p(1), Football = (1-p)(3)", "Row's EV: Opera = q(4), Football = (1-q)(2)", "p = 3 - 3p gives p = 3/4.  4q = 2 - 2q gives q = 1/3."],
                 wrong=lambda v: f"Column: Opera {v[0]:.2f} vs Football {3 * (1 - v[0]):.2f}. Row: Opera {4 * v[1]:.2f} vs Football {2 * (1 - v[1]):.2f}. Each pair must be EQUAL.",
                 ok="Correct, and both probabilities are between 0 and 1, so it is a valid mixture.")],
            pages=[("PROBABILITY DISTRIBUTIONS: every probability must be at least 0 and at most 1, and all probabilities must sum to 1. After solving a mixed equilibrium, ALWAYS check this.", None),
                   ("GENERALIZED BATTLE OF THE SEXES: if (O,O) pays (a, b), (F,F) pays (c, d) and mismatches pay 0, the mixed equilibrium is p = d / (b + d) and q = c / (a + c). With letters instead of numbers the method is the same, and you prove the result lies between 0 and 1.", None)])],
        "LESSON - GENERALIZED GAMES: even with letters instead of numbers you use the same indifference method. A mixed equilibrium exists only if each probability lands between 0 and 1.",
        [Q("Which set of numbers can be a probability distribution over two actions?", ["0.3 and 0.7", "0.6 and 0.6", "1.2 and -0.2", "0.5 and 0.4"], 0, "Each is between 0 and 1 and they sum to 1.", "Check both rules: each in [0,1], and the sum is 1."),
         Q("After solving a mixed equilibrium, what must you verify?", ['Each probability lies between 0 and 1', 'Each probability is more than one half', 'The payoffs add up to exactly one', 'Both players mix in the same way'], 0, "Otherwise the 'mixture' is not a valid probability distribution.", "Think about what a probability can be.")]),

    lvl("Penalty Kicks", "Pete the Parrot", "tide",
        [("E", "Prrrk! Penalty kick. The kicker is stronger on the RIGHT. Numbers are scoring chances out of 10 for the kicker (goalie gets 10 minus that)."),
         ("Y", "Guess I'd kick right all the time...")],
        [lambda: Calc("tide", "Level 15 - Soccer Penalty Kicks", [
            dict(prompt="Find the mixed equilibrium. p = kicker's chance of kicking LEFT (makes the goalie indifferent). q = goalie's chance of diving LEFT (makes the kicker indifferent).",
                 matrix=(PEN, PR, PC), fields=[("p (kicker kicks Left) =", 0.6), ("q (goalie dives Left) =", 0.2)],
                 hints=["Goalie earns: dive Left = 5p + 1(1-p) ; dive Right = 3p + 4(1-p)", "Kicker earns: kick Left = 5q + 7(1-q) ; kick Right = 9q + 6(1-q)", "1 + 4p = 4 - p gives p = 0.6.  7 - 2q = 6 + 3q gives q = 0.2."],
                 wrong=lambda v: f"Goalie: dive Left {5 * v[0] + (1 - v[0]):.2f} vs dive Right {3 * v[0] + 4 * (1 - v[0]):.2f}. Kicker: Left {5 * v[1] + 7 * (1 - v[1]):.2f} vs Right {9 * v[1] + 6 * (1 - v[1]):.2f}. Each pair must be EQUAL.",
                 ok="Correct! Surprise: the kicker aims at his WEAKER side (Left) 60% of the time."),
            dict(prompt="What is the kicker's expected payoff (scoring chance out of 10) in this equilibrium?",
                 matrix=(PEN, PR, PC), fields=[("Kicker's payoff =", 6.6)], tol=0.06,
                 hints=["Use the goalie's mix q = 0.2: kicker's payoff from Kick Left = 5(0.2) + 7(0.8)", "= 1 + 5.6 = 6.6. Kick Right gives the same (that is the point of indifference)."],
                 ok="Correct: 6.6 out of 10 (a 66% scoring chance).")],
            pages=[("The goalie naturally dives to the kicker's STRONGER side more often. To keep the goalie indifferent, the kicker must therefore aim at his weaker side more often. Mixed strategies can be weird: making your opponent indifferent causes the unexpected results.", (PEN, PR, PC))])],
        ["LESSON - SOCCER PENALTY KICKS: in the mixed equilibrium the kicker aims for his weaker side MORE often than his stronger side, because the goalie protects the strong side more.",
         "LESSON - KNIFE-EDGE EQUILIBRIA: some equilibria exist only if a parameter takes one exact value. These rest on a knife edge, so they are substantively questionable and we tend to ignore them. Also, whether a mixed equilibrium exists at all can depend on the parameters being large or small."],
        [Q("Which side does the kicker aim at more often in equilibrium?", ["His weaker side, Left", "His stronger side, Right", "Both sides equally often", "Only the middle of the goal"], 0, "The goalie covers the strong side, so the kicker aims weak 60% of the time.", "Use your answer for p."),
         Q("An equilibrium exists only if a parameter equals exactly 3. Theorists usually...", ["ignore such knife-edge equilibria", "treat it as the main prediction", "add noise until it always holds", "ban that parameter from games"], 0, "Equilibria that depend on an exact parameter value are fragile, so we generally ignore them.", "Would a tiny change in the parameter destroy it?")]),

    lvl("Comp. Statics", "Rusty the Raccoon", "tide",
        [("E", "Think the goalie is better at diving Left now? Then the goalie will dive Left more, right? Let's calculate the change instead of guessing.")],
        [lambda: Calc("tide", "Level 16 - Comparative Statics", [
            dict(prompt="The goalie improves: saving a Left kick by diving Left now pays HIM 7 (not 5). Kicker's payoffs are unchanged. Re-solve. p = kicker's chance of kicking Left, q = goalie's chance of diving Left.",
                 matrix=(PEN2, PR, PC), fields=[("New p (kicker kicks Left) =", 3 / 7), ("New q (goalie dives Left) =", 0.2)],
                 hints=["Goalie earns: dive Left = 7p + 1(1-p) ; dive Right = 3p + 4(1-p)", "The kicker's payoffs did not change, so q = 0.2 stays the same", "1 + 6p = 4 - p gives p = 3/7 = 0.4286"],
                 wrong=lambda v: f"Goalie: dive Left {7 * v[0] + (1 - v[0]):.2f} vs dive Right {3 * v[0] + 4 * (1 - v[0]):.2f}. Kicker: Left {5 * v[1] + 7 * (1 - v[1]):.2f} vs Right {9 * v[1] + 6 * (1 - v[1]):.2f}.",
                 ok="Correct! The goalie's own mix did NOT change. The KICKER's mix changed. That is the surprise of mixed strategies.")],
            pages=[("COMPARATIVE STATICS: how equilibrium behavior changes as an exogenous parameter changes. Four steps: (1) solve for the equilibrium, (2) pick the element of interest, (3) take the derivative with respect to the parameter, (4) use its sign to interpret.", None),
                   ("In mixed equilibria, a player's probabilities come from the OTHER player's payoffs. So improving your own payoff changes your opponent's mix, not yours!", None)])],
        ["LESSON - COMPARATIVE STATICS: most of the point of game theory is to find how outputs change when inputs change. In mixed equilibria, changing YOUR payoff changes the OTHER player's equilibrium probabilities.",
         "LESSON - THE SUPPORT OF A MIXED STRATEGY: the support is the set of pure strategies played with positive probability. Every strategy in the support must earn the SAME expected payoff against the opponent's mix, and no strategy outside it can earn more."],
        [Q("If the goalie's own payoff from diving Left rises, whose mixture changes?", ["The kicker's mixture changes", "The goalie's mixture changes", "Both mixtures stay identical", "Neither player mixes any more"], 0, "The kicker must keep the goalie indifferent, and the goalie's payoffs changed.", "Which payoffs determine whose probabilities?"),
         Q("Against a 50/50 mix by the column player, which rows can be in the support (A pays 6,0; B pays 2,4; C pays 3,2)?", ["A and B only", "A, B and C", "C only", "B and C only"], 0, "A = 3, B = 3, C = 2.5. Only the strategies with the highest expected payoff can be in the support.", "Compute each row's expected payoff against 50/50."),
         Q("Why must all strategies in the support earn the same expected payoff?", ['Otherwise she would play only the best', 'Because every payoff is always equal', 'Because mixing is random in any case', 'Because her opponent demands it of her'], 0, "If one beat the others she would play only it and the mixture would not be a best response.", "What would a rational player do with an inferior option?")]),

    lvl("Weak Dom. Trick", "Pete the Parrot", "tide",
        [("E", "Prrrk! A rare day when weak dominance is USEFUL. Listen: what if the opponent mixes among ALL her strategies?")],
        [lambda: Calc("tide", "Level 17 - The Weak Dominance Trick", [
            dict(prompt="Bottom weakly dominates Top. Suppose the column player mixes 50/50 between Left and Right (she plays ALL her strategies). Find the row player's expected payoff from Top and from Bottom.", matrix=(WEAK, ["Top", "Bottom"], LR),
                 fields=[("EV(Top) =", 1), ("EV(Bottom) =", 1.5)], hints=["EV(Top) = 0.5(2) + 0.5(0)", "EV(Bottom) = 0.5(2) + 0.5(1)", "Top = 1, Bottom = 1.5"], ok="Correct: Top is STRICTLY worse (1 vs 1.5) as soon as she plays Right with any positive probability.")])],
        "LESSON - A TRICK WITH WEAK DOMINANCE: if your opponent mixes among ALL her strategies, a weakly dominated strategy produces a STRICTLY worse payoff than the strategy that dominates it. So you could never play the weakly dominated strategy in an equilibrium where the opponent fully mixes.",
        [Q("If the opponent mixes among all her strategies, a weakly dominated strategy of yours gives...", ["a strictly lower expected payoff", "the same expected payoff", "a strictly higher expected payoff", "an undefined expected payoff"], 0, "The dominating strategy is better against at least one of her strategies, and she plays that one with positive probability.", "Weakly dominated means never better and sometimes worse. Does she ever play the 'sometimes' case?"),
         Q("So can a weakly dominated strategy appear in a full-mixing equilibrium?", ["No, it cannot be played there", "Yes, it always can be played", "Only if all payoffs tie", "Only in zero-sum games"], 0, "It would earn strictly less than its dominator, so it is not a best response.", "Is a strictly worse action ever a best reply?")],
        matrix_extra(WEAK, ["Top", "Bottom"], LR)),

    lvl("Rock Paper Scissors", "Bongo the Baboon", "tide",
        [("E", "Ooh ooh! Rock, Paper, Scissors! I love Rock. Almost 60% of the time. I can't help it.")],
        [lambda: MatrixPlay(dict(title="Level 18 - Rock Paper Scissors", theme="tide", short="Bongo", rows=RPSN, cols=RPSN, pay=RPS, rounds=10,
                                 enemy=lambda h, i, t: random.choices([0, 1, 2], [0.6, 0.2, 0.2])[0], goal=GOAL_TIE.format("Bongo"),
                                 tip="Bongo favours Rock. Exploit him! (Real equilibrium play would be unpredictable.)"))],
        "LESSON - ROCK PAPER SCISSORS: there is no pure equilibrium, and the only equilibrium is to mix one third each. It is a SYMMETRIC ZERO-SUM game: both players have the same options and one's gain is the other's loss. In such games the equilibrium payoff is ZERO for both (each player can copy the other's mix).",
        [Q("In ordinary Rock Paper Scissors, what is each player's equilibrium mix?", ["One third on each action", "Half Rock and half Paper", "Always Paper against Rock", "Two thirds on Rock"], 0, "Any other mix can be exploited.", "Which mix leaves the opponent indifferent among all three?"),
         Q("In a symmetric zero-sum game, what is each player's equilibrium payoff?", ["Zero", "One", "The largest payoff", "Minus one"], 0, "Each player can copy the other's strategy, guaranteeing at least zero, and the payoffs sum to zero.", "What happens if both just copy each other?")],
        matrix_extra(RPS, RPSN, RPSN)),

    lvl("Modified RPS", "Bongo the Baboon", "tide",
        [("E", "I added a rule: Rock beating Scissors is worth 2! Same game, nastier math. Find the equilibrium mix.")],
        [lambda: Calc("tide", "Level 19 - Modified Rock Paper Scissors", [
            dict(prompt="Find the mixed equilibrium. r, p, s = chance of Rock, Paper, Scissors. Because the game is symmetric and zero-sum, make each action earn 0.",
                 matrix=(MRPS, RPSN, RPSN), fields=[("r (Rock) =", 0.25), ("p (Paper) =", 0.5), ("s (Scissors) =", 0.25)],
                 hints=["Your EV: Rock = -p + 2s ; Paper = r - s ; Scissors = -2r + p. Set each to 0.", "Paper: r = s.  Rock: p = 2s.  Check Scissors: p = 2r.", "Sum is 1: s + 2s + s = 1, so s = 1/4, r = 1/4, p = 1/2"],
                 wrong=lambda v: f"Against your guess the actions earn: Rock {-v[1] + 2 * v[2]:.2f}, Paper {v[0] - v[2]:.2f}, Scissors {-2 * v[0] + v[1]:.2f}. All must be equal (0), and r + p + s = {v[0] + v[1] + v[2]:.2f} must be 1.",
                 ok="Correct! (Rock 1/4, Paper 1/2, Scissors 1/4). Paper is played most.")],
            pages=[("MODIFIED ROCK PAPER SCISSORS: there is no pure equilibrium, and no equilibrium where a player mixes between exactly TWO strategies. Nash's theorem guarantees an equilibrium exists, so it must mix among ALL THREE strategies.", (MRPS, RPSN, RPSN)),
                   ("MIXING AMONG THREE: make the opponent indifferent among all three actions (set their expected payoffs equal), add the condition that the probabilities sum to 1, and solve the system.", None)])],
        "LESSON - MIXING AMONG THREE STRATEGIES: set the opponent's expected payoffs for all three actions equal, add 'probabilities sum to 1', and solve. Check every probability is between 0 and 1.",
        [Q("Which action is played most often in this equilibrium?", ["Paper, half of the time", "Rock, since it wins biggest", "Scissors, since it loses most", "All three equally often"], 0, "Rock and Scissors are each 1/4, Paper is 1/2.", "Use your answers for r, p and s."),
         Q("How do you pin down a three-strategy equilibrium mix?", ['Equalize expected payoffs, then require sum one', 'Give each of the actions exactly one third', 'Maximize the single largest payoff in the table', 'Delete two of the actions, then mix the last'], 0, "Indifference equations plus the sum condition determine the mix.", "What did you set equal in the hints?")]),
]
