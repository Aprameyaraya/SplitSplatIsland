"""Regions 4-9: Infinite Strategy Spaces, Expected Utility, Repeated Games, Bayesian Nash, Perfect Bayesian, Finale."""
from sp_engine import *

SG = [[(3, 3), (0, 5)], [(5, 0), (1, 1)]]
SR = ["Share", "Grab"]


def e_moe(h, i, t):
    return 1 if (i == t - 1 or any(r == 1 for r, _ in h)) else 0


def e_grim(h, i, t):
    return 1 if any(r == 1 for r, _ in h) else 0


def e_tft(h, i, t):
    return 0 if not h else h[-1][0]


def mood_grim(h):
    return ("FURIOUS (grim trigger pulled)", RED) if any(r == 1 for r, _ in h) else ("trusting", GREEN)


def mood_tft(h):
    return ("copying your last move", GREEN if not h or h[-1][0] == 0 else RED)


AVG25 = dict(win=lambda sc, n: sc[0] / max(1, n) >= 2.5, goal="Goal: average at least 2.5 points per round to move on.")

def _job(tasks, intro):
    wage, cost = [4, 2], [[1, 0], [3, 0]]
    return dict(title="The Job Market Signal", theme="marsh", intro=intro, types=[("High-skill", 0.6), ("Low-skill", 0.4)],
                acts=["Get a degree", "No degree"], resp=["Offer the HIGH job (wage 4)", "Offer the LOW job (wage 2)"],
                send=[[[wage[r] - cost[t][a] for r in range(2)] for a in range(2)] for t in range(2)], recv=[[3, 0], [0, 3]], tasks=tasks)


JOB_SEP = _job([("separating", "Find a SEPARATING equilibrium: the two types choose different actions.",
                 "The degree is a credible signal because it is too costly for the low-skill type to fake. On the path beliefs are 0 or 1.")],
               "A degree costs a high-skill worker 1 but a low-skill worker 3. Employers see only the degree, then offer the high job (wage 4) or the low job (wage 2); they earn 3 when the job matches the worker. Tap each type's action, then test.")
JOB_POOL = _job([("pool1", "Find a POOLING equilibrium where BOTH types skip the degree. Choose the off-path belief about a degree holder carefully.",
                  "Both skip the degree. On the path the employer's belief equals the prior; off the path any belief that deters deviation works.")],
                "Same job market. Now make both types do the SAME thing. Off the path, beliefs can be anything.")
BQ = dict(title="Beer-Quiche", theme="marsh",
          intro="The sender is a Real Man (90%) or a Wimp (10%). Real men prefer Beer, wimps prefer Quiche (+1 for the preferred breakfast). The receiver chooses Fight or Don't fight: fighting a Wimp pays her +1, fighting a Real Man costs her 1. The sender gets +2 if NOT fought.",
          types=[("Real Man", 0.9), ("Wimp", 0.1)], acts=["Beer", "Quiche"], resp=["Fight", "Don't fight"],
          send=[[[(1 if a == 0 else 0) + (2 if r == 1 else 0) for r in range(2)] for a in range(2)],
                [[(1 if a == 1 else 0) + (2 if r == 1 else 0) for r in range(2)] for a in range(2)]], recv=[[-1, 0], [1, 0]],
          tasks=[("pool0", "Find a pooling equilibrium where BOTH types drink Beer.", "It works if, after seeing Quiche, the receiver believes the sender is probably a Wimp and fights."),
                 ("pool1", "Now find a pooling equilibrium where BOTH types eat Quiche.", "This also needs the off-path belief that a Beer drinker is probably a Wimp. Many theorists find that belief unreasonable, which motivates equilibrium refinements.")])


REGION4 = [
    lvl("No Equilibria", "Sheldon the Snapper", "rope",
        [("E", "Snap! Welcome to the Bottomless Chasm. Here you may name ANY number below 1, and the HIGHER number wins. Name yours."),
         ("Y", "0.9? Then he says 0.99... then I say 0.999...")],
        [],
        ["LESSON - A GAME WITH NO EQUILIBRIA: Nash's theorem says every game with a FINITE number of players and a FINITE number of pure strategies has at least one Nash equilibrium. With infinitely many strategies, there may be none. Without matrices or trees we need new tools.",
         "LESSON - DUELS: in the classic noisy duel each duelist has one shot and accuracy rises as they approach. A shot taken too early is likely to miss, but waiting risks being shot first. The equilibrium has someone shoot at the moment when the two accuracies add up to one."],
        [Q("In 'name any number below 1, higher wins', is there a best response to 0.9?", ['No, a higher one always exists', 'Yes, naming 0.91 is the best answer', 'Yes, naming 0.99 is the best answer', 'Yes, naming 1.0 is the best answer'], 0, "Whatever you name, a slightly bigger number beats it, so no best response exists and no equilibrium exists.", "Is there a LARGEST number below 1?"),
         Q("What does this game show about infinite strategy spaces?", ["Pure equilibria may fail to exist", "Equilibria always exist anyway", "Mixed strategies are impossible", "The count must always be even"], 0, "Nash's existence theorem needs finitely many strategies.", "Which assumption of Nash's theorem is broken?"),
         Q("Both duelists have accuracy t/10 at step t (noisy duel). When does the equilibrium shot happen?", ['Step 5, where they sum to one', 'Step 0, before anyone moves at all', 'Step 10, at point blank range now', 'Step 8, near the end of the walk'], 0, "0.5 + 0.5 = 1 at step 5.", "Solve t/10 + t/10 = 1.")],
        info_extra("Game: each player names a number strictly below 1. The higher number wins.", "Think about whether a LARGEST number below 1 exists.", "Accuracy at step t is t/10 for each duelist. Shoot when accuracy sums to 1.")),

    lvl("Median Voter", "Rusty the Raccoon", "rope",
        [("E", "I'm selling ice cream on this beach, which stretches from 0 to 100. Customers walk to the nearest stand. Set up yours!")],
        [lambda: Hotelling("rope")],
        "LESSON - HOTELLING'S GAME AND THE MEDIAN VOTER THEOREM: when two actors compete to be closer to more customers (or voters) than the rival, both end up in the MIDDLE. Each can always creep next to the other on the bigger side, so the only stable spot is the median. NOTE: this is only true with exactly two competitors.",
        [Q("Where do two competing vendors end up in equilibrium?", ["Both at the middle", "Both at the ends", "One at each end", "At random positions"], 0, "Any other spot lets the rival creep in on the bigger side.", "What happened when you stood anywhere except 50?"),
         Q("The median voter result requires...", ["exactly two competitors", "any number of competitors", "customers who dislike the center", "an even number of customers"], 0, "With more than two actors the solution is more complicated.", "Check the takeaway note at the end of the lesson.")],
        info_extra("Customers are spread evenly along a beach from 0 to 100.")),

    lvl("Second Price Auction", "Gorg the Gorilla", "rope",
        [("E", "GRRR. Auction time! The highest bidder wins but pays the SECOND highest bid. You value the vase at 70. Let's compute.")],
        [lambda: Calc("rope", "Level 22 - Second Price Auction", [
            dict(prompt="You value the vase at 70 and bid your true value, 70. The highest OTHER bid is 55. What price do you pay, and what is your profit (value minus price)?",
                 fields=[("Price you pay =", 55), ("Your profit =", 15)], hints=["You win (70 > 55) and pay the SECOND highest bid", "Price = 55, profit = 70 - 55 = 15"], ok="Correct: you pay 55 and gain 15."),
            dict(prompt="Suppose you had SHADED your bid down to 50. The highest other bid is still 55. What is your profit?",
                 fields=[("Your profit =", 0)], hints=["50 < 55 so you do not win", "No win means profit 0"], ok="Correct: you lose a deal that would have paid 15. Shading never helps."),
        ])],
        "LESSON - SECOND PRICE AUCTIONS: bidding your TRUE valuation is an equilibrium. Bidding higher can make you win and pay more than the vase is worth to you; bidding lower can make you lose profitable wins. Your bid never sets your price, so honesty is best. This holds whether or not bidders know each other's valuations.",
        [Q("In a second price auction, what is a good strategy?", ["Bid your true valuation", "Bid far below your value", "Bid far above your value", "Bid exactly zero always"], 0, "Your bid only decides whether you win; the price is set by the second-highest bid.", "Does your bid change the price you pay?"),
         Q("Why not bid above your value?", ['You might win and pay too much', 'You would always lose the item', 'The rules forbid any higher bids', 'It lowers all of the other bids'], 0, "If the second-highest bid exceeds your value, you win at a loss.", "What if the second-highest bid were 80?")]),
]

REGION5 = [
    lvl("Preferences", "Kiki the Kiwi", "cave",
        [("E", "Kiwi! Welcome to Gambler's Cave. To say a player 'maximizes expected utility' her preferences must obey rules. First: she must be able to compare options, and her comparisons must be consistent.")],
        [lambda: MoneyPump("cave")],
        ["LESSON - EXPECTED UTILITY THEORY: expected utilities are a mathematical way to represent preferences. They need four properties: completeness, transitivity, independence over lotteries, and continuity. We begin with the first two.",
         "COMPLETENESS: for any two options, you can say you prefer one or are indifferent. TRANSITIVITY: if A is preferred to B and B to C, then A is preferred to C. Together they are called RATIONALITY. Someone with cyclic preferences can be turned into a money pump."],
        [Q("Completeness requires that...", ["any two options can be compared", "all options are equally good", "preferences never change over time", "every option involves a gamble"], 0, "She must prefer one option or be indifferent.", "Think 'complete list of comparisons'."),
         Q("She prefers apples to bananas, bananas to cherries, and cherries to apples. Which axiom fails?", ["Transitivity", "Completeness", "Continuity", "Independence"], 0, "A > B > C should give A > C, but she prefers C to A. She can be exploited by trades.", "Follow the chain of preferences."),
         Q("Which two properties together are called 'rationality'?", ["Completeness and transitivity", "Independence and continuity", "Risk aversion and neutrality", "Pareto and Condorcet"], 0, "They are the base requirements before lotteries enter.", "Which two did we just define?")],
        info_extra("Axioms so far: completeness (everything is comparable) and transitivity (no cycles).")),

    lvl("Lotteries", "Kiki the Kiwi", "cave",
        [("E", "Now lotteries: gambles with probabilities. If you prefer one lottery to another, mixing both with the SAME third lottery shouldn't flip your choice. That is independence. Let's see whether humans obey it.")],
        [lambda: Calc("cave", "Level 24 - The Allais Paradox", [
            dict(prompt="Allais: A = $1M sure. B = 89% $1M, 10% $5M, 1% $0. C = 11% $1M, 89% $0. D = 10% $5M, 90% $0. Let u($0)=0, u($1M)=1, u($5M)=x. Find the x thresholds that would make the common answers (A over B) and (D over C) hold.",
                 fields=[("A beats B only if x is below", 1.1), ("D beats C only if x is above", 1.1)],
                 hints=["EU(A) = 1.  EU(B) = 0.89(1) + 0.10x + 0.01(0) = 0.89 + 0.10x.  A > B needs 1 > 0.89 + 0.10x, so x < 1.1", "EU(C) = 0.11.  EU(D) = 0.10x.  D > C needs 0.10x > 0.11, so x > 1.1"],
                 ok="Correct! No x satisfies BOTH x < 1.1 and x > 1.1. Many people choose A and D, which no expected utility maximizer can do. That is the Allais paradox: it violates independence.")],
            pages=[("CONDORCET'S PARADOX: three voters rank A>B>C, B>C>A and C>A>B. A beats B (2 to 1), B beats C (2 to 1), but C beats A (2 to 1). Each voter is transitive, yet the group's preferences cycle: social preferences can fail transitivity.", None),
                   ("LOTTERIES are probability distributions over outcomes. INDEPENDENCE: if you prefer lottery X to Y, you should still prefer a coin flip between X and Z to a coin flip between Y and Z. The Allais paradox shows real people often violate this.", None)])],
        "LESSON - LOTTERIES AND INDEPENDENCE: lotteries are probability distributions over outcomes. Completeness and transitivity are not enough, so we add independence (mixing both lotteries with the same third one cannot change your preference). The Allais paradox shows people's common choices violate it.",
        [Q("Condorcet's paradox shows that...", ["group preferences can cycle", "voters are never transitive", "majority rule always works", "every vote ends in a tie"], 0, "Each voter is transitive but the majority outcome is cyclic.", "Check the three pairwise majorities."),
         Q("Independence says that if you prefer X to Y, then you also prefer...", ['a mix of X and Z to a mix of Y and Z', 'Z to both X and Y at the same time', 'Y to X as soon as risk is present', 'a sure thing to every possible lottery'], 0, "Mixing both options with the same third lottery shouldn't flip the preference.", "It is about mixing with a COMMON third lottery."),
         Q("The common choices in the Allais paradox (A over B, D over C)...", ['cannot come from any expected utility', 'always come from simple risk aversion', 'show that everyone is fully transitive', 'are strictly dominated in this problem'], 0, "They require x < 1.1 and x > 1.1 at once.", "Look at your two thresholds.")]),

    lvl("Utility & Risk", "Kiki the Kiwi", "cave",
        [("E", "Last room: if preferences obey the four axioms, utilities exist. But how do those utilities describe your attitude to RISK? And which transformations keep your choices the same?")],
        [lambda: Calc("cave", "Level 25 - Risk Attitudes", [
            dict(prompt="Your utility is u(x) = sqrt(x). A lottery pays 100 with probability 0.5 and 0 with probability 0.5. Find the expected utility and the certain amount (certainty equivalent) you consider equally good.",
                 fields=[("Expected utility =", 5), ("Certainty equivalent =", 25)],
                 hints=["EU = 0.5 sqrt(100) + 0.5 sqrt(0) = 0.5(10) = 5", "A sure amount c with sqrt(c) = 5 gives c = 25"],
                 ok="Correct! The lottery's expected value is 50 but you accept just 25 for sure: you are RISK AVERSE."),
            dict(prompt="Replace the utility with v(x) = 2 sqrt(x) + 3 (multiply by a positive number and add a constant). What is the expected utility of the same lottery?",
                 fields=[("New expected utility =", 13)],
                 hints=["EU(v) = 2(EU of sqrt) + 3 = 2(5) + 3", "= 13. The ranking of lotteries is unchanged."],
                 ok="Correct: positive affine transformations keep every ranking the same.")],
            pages=[("CONTINUITY: there are no infinitely good or infinitely bad prizes. If A > B > C, some mixture of A and C is exactly as good as B. With completeness, transitivity, independence and continuity, preferences can be represented by expected utility.", None)])],
        ["LESSON - EXPECTED UTILITY TRANSFORMATIONS: multiplying utilities by a positive number and adding a constant leaves choices unchanged. Squaring or taking roots can change them.",
         "LESSON - RISK ATTITUDES: if a sure amount is preferred to a gamble with the same expected value, the person is RISK AVERSE (concave utility). Indifferent means risk neutral (linear), and preferring the gamble means risk acceptant (convex). PARETO EFFICIENCY: an outcome is Pareto efficient if nobody can be made better off without making someone worse off."],
        [Q("A risk averse person has a utility function that is...", ["concave, bending downward", "linear, a straight line", "convex, bending upward", "constant at every level"], 0, "Concavity means the sure amount is preferred to the gamble.", "Recall the sqrt(x) example."),
         Q("An outcome is Pareto efficient if...", ['nobody can gain without another losing', 'everyone receives exactly equal payoffs', "it maximizes only one player's payoff", 'it is also a Nash equilibrium of the game'], 0, "There is no change that makes someone better off at nobody's expense.", "Think 'no free improvements'."),
         Q("Which change to utilities keeps every ranking of lotteries?", ['Scale by a positive number, add a constant', 'Square each of the utility numbers in the table', 'Take the square root of every utility number', 'Reverse the sign of every single utility number'], 0, "Positive affine transformations preserve expected utility rankings.", "Recall your answer to the v(x) problem.")]),
]

REGION6 = [
    lvl("Finite Repeats", "Moe the Monkey", "jungle",
        [("E", "Ooh ooh! Bananas! We'll play Share or Grab exactly THREE times, and you know it. Cooperate with me and I'll cooperate with you.")],
        [lambda: MatrixPlay(dict(title="Level 26 - Repeated Prisoner's Dilemma (finite)", theme="jungle", short="Moe", rows=SR, cols=SR, pay=SG, rounds=3, enemy=e_moe, goal=GOAL_TIE.format("Moe"),
                                 tip="Same Share/Grab table, three stages, known end. Moe says he's friendly... can you still finish level with him?"))],
        "LESSON - REPEATED PRISONER'S DILEMMA (FINITE): in the last round nothing remains to reward or punish, so both Grab. Then round 2 is effectively the last, and so on: cooperation UNRAVELS by backward induction. In any finite repeated Prisoner's Dilemma the only SPE is to defect every round.",
        [Q("The last round arrives. What do rational players choose?", ["Grab, since no future remains", "Share, hoping to be repaid", "Flip a coin each time", "Copy whatever round two was"], 0, "In the final round it is just the one-shot game.", "After the last round, is there any future to protect?"),
         Q("What is the subgame perfect outcome of the three rounds?", ["Grab in all three rounds", "Share, Share, then Grab last", "Share in all three rounds", "Whatever Moe's mood decides"], 0, "Backward induction unravels all the way back to round 1.", "Apply the same logic round by round, starting from the end.")]),

    lvl("Discounting", "Bongo the Baboon", "jungle",
        [("E", "Ooh ooh! A banana tomorrow is worth less to me than a banana today. How much less? That's my discount factor, delta.")],
        [lambda: Calc("jungle", "Level 27 - Discount Factors and Infinite Payoffs", [
            dict(prompt="Cooperation pays 3 every round forever. The discount factor is d = 0.9 (a payoff t rounds from now is multiplied by d^t). What is the total value of cooperating forever?",
                 fields=[("Total value =", 30)], hints=["3 + 3d + 3d^2 + ... = 3(1 + d + d^2 + ...) = 3 / (1 - d)", "3 / (1 - 0.9) = 3 / 0.1 = 30"], ok="Correct: 3 / (1 - d) = 30."),
            dict(prompt="Now you Grab once (payoff 5), get punished with mutual Grab (payoff 1) for every round after, and d = 0.9. What is the total value?",
                 fields=[("Total value =", 14)], hints=["5 now, then 1d + 1d^2 + ... = d / (1 - d)", "5 + 0.9 / 0.1 = 5 + 9 = 14"], ok="Correct: 5 + d / (1 - d) = 14, far less than 30.")],
            pages=[("The DISCOUNT FACTOR d (between 0 and 1) says how much players value the future. Near 1 means patient, near 0 means impatient. The GEOMETRIC SERIES: 1 + d + d^2 + ... = 1 / (1 - d). So a constant payoff x every round forever is worth x / (1 - d).", None)])],
        "LESSON - DISCOUNT FACTORS AND GEOMETRIC SERIES: infinite streams of payoffs can have finite value when discounted. A constant payoff x forever is worth x / (1 - d). The value of cooperating forever and the value of deviating once are both computed this way.",
        [Q("What does a discount factor close to 1 mean?", ["The players are very patient", "The players are very impatient", "The game ends next round", "All payoffs are zero"], 0, "They value the future almost as much as the present.", "d multiplies each later round's payoff."),
         Q("A payoff of 2 every round forever with d = 0.5 is worth...", ["4", "2", "6", "1"], 0, "2 / (1 - 0.5) = 4.", "Use x / (1 - d).")]),

    lvl("Grim Trigger", "Grizelda the Gorilla", "jungle",
        [("E", "GRRR. Same table. NO ONE knows how many rounds: after each there is a 90% chance of another. Cooperate and I cooperate. Betray me ONCE and I Grab until the island sinks.")],
        [lambda: MatrixPlay(dict(title="Level 28 - Grim Trigger", theme="jungle", short="Grizelda", rows=SR, cols=SR, pay=SG, rounds=None, enemy=e_grim, mood=mood_grim,
                                 tip="No known last round. Grizelda cooperates until you Grab. A grim trigger player punishes forever.", **AVG25)),
         lambda: Calc("jungle", "Level 28 - One-Shot Deviation", [
             dict(prompt="One-shot deviation principle: check only a single deviation. Cooperating forever is worth 3 / (1 - d). Grabbing once then being punished is worth 5 + d / (1 - d). Find the smallest discount factor d for which cooperating is at least as good.",
                  fields=[("Minimum d =", 0.5)], hints=["3 / (1 - d) >= 5 + d / (1 - d)", "Multiply by (1 - d): 3 >= 5(1 - d) + d = 5 - 4d", "4d >= 2, so d >= 1/2"], ok="Correct: players must have d of at least 1/2 for grim trigger to sustain cooperation.")])],
        ["LESSON - THE ONE-SHOT DEVIATION PRINCIPLE: a strategy profile is an SPE if and only if no player can gain by deviating at a SINGLE stage and following the strategy everywhere else. So instead of checking infinitely many deviations, check one.",
         "LESSON - GRIM TRIGGER: begin by cooperating; if anyone ever defects, defect forever. To check it is an SPE: (1) mutual defection in the punishment subgame is Nash, so punishing is credible; (2) in each cooperative period, no one wants a one-shot deviation. This holds for d large enough."],
        [Q("What does the one-shot deviation principle let you do?", ["Check only single deviations", "Ignore all future payoffs", "Skip the punishment subgame", "Assume the game is finite"], 0, "If no one-stage deviation helps, no deviation does.", "Why did you compare only two numbers?"),
         Q("Why is Grizelda's punishment credible?", ['Grab/Grab is Nash in every later subgame', 'She is simply angrier than all the others', 'She has promised it in writing to everyone', 'Punishing never costs her anything at all'], 0, "Mutual defection is an equilibrium of the stage game, so it is a best reply forever.", "Check step 1 of the grim trigger test."),
         Q("When is grim trigger an SPE of the repeated Prisoner's Dilemma?", ["When players are patient enough", "When there is a known last stage", "When payoffs are exactly equal", "When defections cannot be seen"], 0, "d must be at least the threshold you computed.", "Recall your minimum d.")]),

    lvl("Tit-for-Tat", "Gorg the Gorilla", "jungle",
        [("E", "GRRR. I play Tit-for-Tat: I start with Share and then copy whatever YOU did last round. Forgiving, but fair.")],
        [lambda: MatrixPlay(dict(title="Level 29 - Tit-for-Tat", theme="jungle", short="Gorg", rows=SR, cols=SR, pay=SG, rounds=None, enemy=e_tft, mood=mood_tft,
                                 tip="Gorg copies your last move. Cooperation can survive, but what does a single Grab do?", **AVG25))],
        "LESSON - TIT-FOR-TAT: it is a Nash equilibrium for patient players, and it is nicer than grim trigger because it forgives. But it is NOT subgame perfect. After a deviation the players alternate (one cooperates while the other defects). The player who is supposed to defect would rather cooperate and restart permanent cooperation. That is only unprofitable for exactly one discount factor (a knife-edge), so tit-for-tat is almost never subgame perfect.",
        [Q("Is tit-for-tat subgame perfect in the repeated Prisoner's Dilemma?", ['Only for one exact discount factor', 'Yes, for every discount factor ever', 'No, for every discount factor ever', 'Only when the game is finite'], 0, "The condition for punishing is the flipped version of the condition for cooperating, so both hold only at a knife-edge.", "Recall the knife-edge lesson."),
         Q("Why does the tit-for-tat punishment fail?", ['The punisher prefers restoring cooperation', 'The punisher gains from defecting forever', 'Punishment can never be observed at all', 'The game ends before punishment can start'], 0, "Switching back to cooperating ends the alternating sequence and brings back 3 every round.", "What does the player who must 'sucker' the other do?")]),

    lvl("Folk Theorem", "Moe the Monkey", "jungle",
        [("E", "Ooh ooh! In these infinite games there isn't just ONE equilibrium. There are zillions!")],
        [lambda: Calc("jungle", "Level 30 - How Patient Must Players Be?", [
            dict(prompt="Target path: both cooperate for payoff 2 per round (less than the full 3). A one-shot deviation pays 5 once, then the punishment payoff is 1 forever (the stage Nash payoff). Find the smallest discount factor d that sustains the path.",
                 fields=[("Minimum d =", 0.75)], hints=["Path: 2 / (1 - d).  Deviation: 5 + d / (1 - d)", "2 >= 5(1 - d) + d = 5 - 4d", "4d >= 3, so d >= 3/4"], ok="Correct: d >= 0.75. A smaller reward from cooperating needs MORE patience. By the folk theorem there is a threshold for every outcome that beats the stage Nash payoffs.")])],
        ["LESSON - THE FOLK THEOREM: take a Nash equilibrium of the stage game and any alternative set of strategies that gives EVERY player a strictly higher stage payoff. If d is high enough, there is an SPE in which players use the alternative strategies on the path of play, enforced by the credible threat of reverting to the stage Nash equilibrium. The minimum d compares the equilibrium-path payoff with the best deviation plus the Nash payoff forever.",
         "LESSON - THE PREDICTION PROBLEM: for patient enough players almost any stream of outcomes can be an equilibrium, even long streams of the 'sucker's payoff' for one player. So game theory used to PREDICT behavior says little here, though it still helps to prescribe."],
        [Q("The folk theorem says that for patient enough players...", ["many outcomes are SPE", "only mutual defection survives", "only cooperation survives", "equilibria no longer exist"], 0, "The set of equilibria is huge.", "Think 'zillions of equilibria'."),
         Q("How is a better-than-Nash outcome supported?", ['By threatening to revert to the stage Nash', 'By banning every deviation through the law', 'By making every single payoff identical', 'By ending the game before it gets going'], 0, "Reverting is credible because the stage Nash equilibrium is an equilibrium.", "What was the grim trigger threat?"),
         Q("What is the 'prediction problem'?", ['Almost any outcome can be an equilibrium', 'No equilibrium exists in these games', 'Players cannot compute their own payoffs', 'Equilibria are always unique and obvious'], 0, "With so many equilibria, theory struggles to predict which will occur.", "What follows from 'zillions of equilibria'?")]),
]

REGION7 = [
    lvl("Incomplete Info", "Kiki the Kiwi", "temple",
        [("E", "Kiwi! In this temple nobody knows who they face. Fighters attack, wimps hide. Nature picks which one you meet, and the guard must decide whether to defend.")],
        [lambda: Calc("temple", "Level 31 - Bayesian Nash Equilibrium", [
            dict(prompt="Nature draws the intruder: Fighter (probability 0.6) who always Attacks, or Wimp (0.4) who always Hides. The guard earns: Defend = +2 vs Attack and -1 vs Hide. Ignore = -1 vs Attack and +1 vs Hide. Find the guard's expected payoff from each action.",
                 fields=[("EV(Defend) =", 0.8), ("EV(Ignore) =", -0.2)],
                 hints=["EV(Defend) = 0.6(2) + 0.4(-1) = 1.2 - 0.4", "EV(Ignore) = 0.6(-1) + 0.4(1) = -0.6 + 0.4", "Defend = 0.8, Ignore = -0.2"], ok="Correct: the guard best-responds by Defending."),
            dict(prompt="If q is the probability the intruder attacks, the guard is indifferent at some q*. Find it.",
                 fields=[("q* =", 0.4)], hints=["Defend: 2q - (1 - q) = 3q - 1", "Ignore: -q + (1 - q) = 1 - 2q", "3q - 1 = 1 - 2q gives q = 0.4"], ok="Correct: with q above 0.4 the guard defends.")],
            pages=[("INCOMPLETE INFORMATION: a player may not know the other's payoffs. Harsanyi's trick: Nature moves first and draws each player's TYPE. A BAYESIAN NASH EQUILIBRIUM needs a strategy for EVERY type of every player, such that each type best-responds given beliefs about the others' types.", None)])],
        "LESSON - BAYESIAN NASH EQUILIBRIUM: with several types, previous solution concepts are insufficient. A BNE is a Nash equilibrium of the game where Nature draws types first: each type chooses a best response, and uninformed players best-respond to the distribution of types' actions. You can solve it with ordinary Nash techniques on the expanded game.",
        [Q("A Bayesian Nash equilibrium requires...", ['a strategy for every type of every player', 'a strategy only for the average type', "beliefs that ignore Nature's draw entirely", 'pure strategies from every player involved'], 0, "Every type must best-respond.", "How many sets of strategies did the Fighter and Wimp each need?"),
         Q("In Harsanyi's approach, who moves first?", ['Nature, drawing types', 'The informed player first', 'The uninformed player first', 'Nobody moves at first'], 0, "Nature's draw turns incomplete information into imperfect information.", "Who decides the types?")]),

    lvl("Dominance & Types", "Kiki the Kiwi", "temple",
        [("E", "Dominance returns, now with types. Ex ante: before you know your type. Interim: after you learn it.")],
        [lambda: Calc("temple", "Level 32 - Ex Ante vs Interim", [
            dict(prompt="Before learning her type (ex ante) a player is type A with probability 0.75 and type B with 0.25. ACT pays 4 to type A and -2 to type B. PASS pays 1 to both. Find the ex ante expected payoff of each.",
                 fields=[("EV(Act) =", 2.5), ("EV(Pass) =", 1)], hints=["EV(Act) = 0.75(4) + 0.25(-2)", "= 3 - 0.5 = 2.5", "EV(Pass) = 1"],
                 ok="Correct: ex ante, Act (2.5) beats Pass (1). But type B, interim, prefers Pass (1 beats -2). Ex ante and interim views can disagree.")])],
        "LESSON - EX ANTE AND INTERIM DOMINANCE: a strategy is EX ANTE dominated if another strategy gives a higher expected payoff whatever the others do (evaluated before learning your type). It is INTERIM dominated for a type if another action does better for that type. If a strategy is interim dominated, it is ex ante dominated, but not the reverse. Strictly dominated strategies (either kind) can be deleted without losing any BNE; the weak-dominance caveat still applies.",
        [Q("Ex ante dominance evaluates a strategy...", ["before the player learns her type", "after the player learns her type", "only for the strongest type", "only in two-player games"], 0, "The ex ante view is the plan formed before types are known.", "'Ante' means before."),
         Q("Which implication is correct?", ["Interim dominance implies ex ante dominance", "Ex ante dominance implies interim dominance", "Both always imply each other", "Neither ever implies the other"], 0, "If every type's action is dominated, the whole plan is dominated, but the converse can fail.", "Which one is the stronger, type-by-type condition?"),
         Q("May you delete strictly dominated strategies in Bayesian games?", ["Yes, without losing any BNE", "No, never under any condition", "Only the ex ante kind", "Only in zero-sum games"], 0, "The usual rule for strict dominance carries over.", "Recall the rule from Unit 1.")]),

    lvl("Poker & Info", "Gorg the Gorilla", "temple",
        [("E", "GRRR. Poker. Each player draws one card from ace down to 2. Both bet $1 or fold. Higher card wins. Who should bet?")],
        [lambda: Unravel("temple")],
        ["LESSON - WHY ARE THERE ANTES IN POKER? The ace has a weakly dominant strategy to bet. The 2 has a weakly dominant strategy to fold. Once 2 folds, the 3 can win only against a 2 that bets, so 3 folds, then 4, and so on all the way up to the king. Only the ace bets! This is the UNRAVELING principle. Antes put money in the pot so that weaker hands are tempted to bet.",
         "LESSON - IS MORE INFORMATION ALWAYS BETTER? In a single-person decision, more information cannot hurt. In games, extra information changes what others expect and how they respond, so more information can make a player worse off."],
        [Q("In the poker game, which types end up betting?", ["Only the ace", "Every card above average", "Only the king and ace", "Every card, always"], 0, "Unraveling: everyone else prefers to fold.", "Start with the ace and the 2, then work inward."),
         Q("Why do poker games use antes?", ['Money in the pot tempts weak hands', 'Antes make the dealt cards random', 'Antes speed up the process of dealing', "Antes increase everyone's information"], 0, "Without it the unraveling logic makes all but the best hand fold.", "What changes when there is already money to win?"),
         Q("In strategic games, can more information hurt a player?", ["Yes, others may respond differently", "No, never in any game", "Only in zero-sum games", "Only when there are three players"], 0, "Information changes others' beliefs and actions too.", "In one-player decisions it cannot hurt. What changes with others?")]),

    lvl("Cutpoints", "Rusty the Raccoon", "temple",
        [("E", "Each of us has a secret cost c between 0 and 1, evenly spread. Acting pays 1 if the other doesn't act and 0 if she does, minus your cost. Who acts?")],
        [lambda: Calc("temple", "Level 34 - Cutpoint Strategies", [
            dict(prompt="Each player acts only if her cost c is below a cutpoint x. If the other player acts with probability x, acting pays (1 - x) - c in expectation. Find the symmetric cutpoint x.",
                 fields=[("Cutpoint x =", 0.5)], hints=["Indifferent type: (1 - x) - x = 0", "1 - x = x, so x = 0.5"], ok="Correct: every player with c below 0.5 acts. Each acts half the time, observationally like a mixed strategy!")],
            pages=[("CONTINUOUS TYPES: with infinitely many types, a BNE needs an action for every type. Fortunately equilibria tend to follow a CUTPOINT rule: all types below a cutpoint play one action, all above play the other.", None)])],
        ["LESSON - CONTINUOUS TYPES AND CUTPOINT STRATEGIES: equilibria tend to follow a cutpoint rule. Cutpoint strategies look like mixed strategies from outside, but the randomness comes from Nature's draw of type rather than the player's own randomization.",
         "LESSON - THE PURIFICATION THEOREM: almost all mixed strategy Nash equilibria of a complete information game are the limit of PURE strategy Bayesian Nash equilibria when a small amount of private payoff uncertainty is added and then shrinks to zero. So mixing can be interpreted as uncertainty over types (Harsanyi purification)."],
        [Q("What shape do equilibria usually take with continuous types?", ["A cutpoint rule", "A uniform random rule", "A rule that ignores types", "A rule with no pattern at all"], 0, "Types below the cutpoint do one thing, types above do another.", "Think about your answer x."),
         Q("The purification theorem says mixed equilibria can be seen as...", ['limits of pure equilibria with small noise', 'mistakes that the players make by accident', 'equilibria that exist in zero-sum games only', 'equilibria that lack any best responses'], 0, "The randomness is reinterpreted as Nature's draw of types.", "Where does the randomness come from in a cutpoint equilibrium?")]),

    lvl("Bayes & Curse", "Gorg the Gorilla", "temple",
        [("E", "GRRR. Evidence arrives. How should beliefs change? Bayes' rule! Then we'll see how winning can be bad news.")],
        [lambda: Calc("temple", "Level 35 - Bayes' Rule", [
            dict(prompt="10% of travelers are smugglers. The scanner flags 90% of smugglers and 20% of innocents. A traveler is flagged. What is the probability she is a smuggler?",
                 fields=[("P(smuggler | flagged) =", 1 / 3)],
                 hints=["P(smuggler and flagged) = 0.10 x 0.90 = 0.09", "P(innocent and flagged) = 0.90 x 0.20 = 0.18", "0.09 / (0.09 + 0.18) = 1/3"], ok="Correct: 1/3. Updating beliefs with Bayes' rule is the core of the next unit.")],
            pages=[("BAYES' RULE: P(type | signal) = P(signal | type) x P(type) / P(signal). Use it to update beliefs whenever new evidence arrives.", None)])],
        "LESSON - THE WINNER'S CURSE: with a COMMON value good (an oil field), others' information matters to YOU. If you win a second price auction, the other bidders had lower estimates, so your updated estimate of the value is lower than before winning. Bidding your raw estimate is therefore not an equilibrium. Bid your value conditional on WINNING, which means shading below your raw estimate.",
        [Q("When you win a common-value auction, your updated estimate of its value is...", ["lower than your original estimate", "higher than your original estimate", "exactly equal to the original", "unrelated to the original"], 0, "Winning tells you the other bidders had lower estimates.", "What does it reveal about others' information?"),
         Q("How should you bid in a common-value second price auction?", ["Below your raw estimate", "Exactly at your raw estimate", "Above your raw estimate", "At zero every time"], 0, "Bid the value conditional on winning.", "What is the cure for the winner's curse?")]),
]

REGION8 = [
    lvl("PBE & Screening", "Sheldon the Snapper", "marsh",
        [("E", "Snap! Welcome to the Foggy Marsh. Here we need beliefs. I'm selling a used car: half are good, half are lemons. You (the buyer) move first. You can't tell which is which.")],
        [lambda: Calc("marsh", "Level 36 - Screening and Adverse Selection", [
            dict(prompt="A buyer values a good car at 12 and a bad car at 4. Half of all cars are good. The seller of a good car will accept no less than 10, a bad car owner no less than 2. What is the most the buyer will pay for a car of unknown quality?",
                 fields=[("Maximum price =", 8)], hints=["Expected value = 0.5(12) + 0.5(4)", "= 6 + 2 = 8"], ok="Correct: 8. But who will sell at 8?")],
            pages=[("PERFECT BAYESIAN EQUILIBRIUM = STRATEGIES + BELIEFS. Strategies must be sequentially rational given beliefs (credible threats), and beliefs must be updated by Bayes' rule wherever possible. You MUST write beliefs in your answer. Off the path of play, beliefs can be anything.", None),
                   ("SCREENING GAMES: the UNINFORMED player moves first. Her belief is simply the prior, because there is nothing yet to update from. Her action may make different types do different things (screening them).", None)])],
        "LESSON - SCREENING GAMES AND ADVERSE SELECTION: in a screening game the uninformed player moves first, so beliefs are the prior. ADVERSE SELECTION: a price of 8 is below the good owner's minimum 10, so only bad-car owners sell. Buyers, anticipating that, will pay only for bad cars, and the good cars never trade. The market is ruined by the hidden information.",
        [Q("What does a perfect Bayesian equilibrium consist of?", ["Strategies and beliefs, updated by Bayes' rule", 'Strategies only, exactly as in Nash equilibrium', 'Beliefs only, with no strategies attached to them', 'Payoffs and probabilities only, nothing else'], 0, "Writing out the beliefs is required, or the answer is wrong.", "What new ingredient did PBE add to SPE?"),
         Q("In a screening game, what is the uninformed player's belief when she moves?", ["The prior from Nature", "A posterior from a signal", "Certainty about the type", "Whatever is most convenient"], 0, "She moves first, so there is nothing to update from.", "Who moves first in screening?"),
         Q("At a price of 8, which sellers stay in the market?", ["Only owners of bad cars", "Only owners of good cars", "Owners of both kinds", "Nobody at all"], 0, "The good-car owner's minimum is 10 > 8, while the bad-car owner's minimum is 2 < 8.", "Compare the price to each owner's minimum.")]),

    lvl("Separating", "Kiki the Kiwi", "marsh",
        [("E", "Kiwi! A candidate is Strong (30%) or Weak (70%). She sends a signal. The Strong ALWAYS sends it; the Weak sends it 20% of the time. You observe the signal. What do you believe?")],
        [lambda: Calc("marsh", "Level 37 - Signaling and Updating Beliefs", [
            dict(prompt="Prior: Strong 30%, Weak 70%. Strong always signals. Weak signals with probability 0.2. After seeing the signal, what is your posterior probability that she is Strong?",
                 fields=[("P(Strong | signal) =", 0.3 / 0.44)], tol=0.012,
                 hints=["P(Strong and signal) = 0.30 x 1 = 0.30", "P(Weak and signal) = 0.70 x 0.2 = 0.14", "0.30 / (0.30 + 0.14) = 0.30/0.44 = 0.68"], ok="Correct: about 0.68. The signal is informative but not conclusive.")],
            pages=[("SIGNALING GAMES: the INFORMED player moves first, and the uninformed player observes the action and updates beliefs with Bayes' rule. Three families of PBE: SEPARATING (types choose different actions), POOLING (types choose the same action), and SEMI-SEPARATING (one type mixes).", None),
                   ("FINDING SEPARATING EQUILIBRIA: (1) pick a set of separating strategies, (2) find the receiver's best response, (3) check whether any type wants to deviate (pretend to be another type), (4) repeat for other sets. On the path, beliefs are trivial: probability 1 on the type who chose that action.", None)]), lambda: Signal(JOB_SEP)],
        "LESSON - SEPARATING EQUILIBRIUM: types separate by taking distinct actions, so after observing the action the receiver learns the type exactly. The key check: would a type gain by pretending to be the other? If not, the separation holds.",
        [Q("In a separating equilibrium, what does the receiver believe after seeing an action?", ["Probability 1 on that action's type", 'The same prior as before the action', 'An arbitrary belief with no reason', 'Probability one half on each type'], 0, "Separation reveals the type exactly.", "Do different types choose different actions?"),
         Q("What is the key check in a separating equilibrium?", ["No type gains by mimicking another", "All types earn exactly the same payoff", "The receiver ignores the signal", "Both types pick the cheaper action"], 0, "If a type could profit by deviating to the other type's action, separation fails.", "Step 3 of the four-step process.")]),

    lvl("Pooling", "Rusty the Raccoon", "marsh",
        [("E", "What if Strong and Weak do the SAME thing? Then the signal says nothing, and I must decide what to believe if I ever see something ELSE.")],
        [lambda: Calc("marsh", "Level 38 - Off-the-Path Beliefs", [
            dict(prompt="Off the path, the receiver sees an unexpected signal and believes the sender is Good with probability m. Hiring pays 4 if Good and -2 if Bad; not hiring pays 0. Find the smallest m for which hiring is optimal.",
                 fields=[("Smallest m =", 1 / 3)], hints=["EV(hire) = 4m - 2(1 - m) = 6m - 2", "Hire if 6m - 2 >= 0", "m >= 1/3"], ok="Correct: she hires if she believes m >= 1/3. Off the path, ANY belief is allowed by PBE.")],
            pages=[("POOLING: all types take the same action. On the path, the receiver's belief equals the prior. Off the path, Bayes' rule says nothing, so PBE allows ANY belief there. To test a pooling equilibrium: check each type's deviation, note which off-path beliefs keep that type from deviating, then see if some belief works for ALL types.", None)]), lambda: Signal(JOB_POOL)],
        "LESSON - POOLING AND OFF-THE-PATH BELIEFS: in pooling, on-path beliefs equal the prior; off-path beliefs are unrestricted. Because beliefs can be anything off the path, when a pooling equilibrium exists there are usually infinitely many PBE. Find which beliefs deter every type's deviation.",
        [Q("In a pooling equilibrium, the on-path belief equals...", ["the prior from Nature", "certainty about one type", "an arbitrary belief", "the average of all payoffs"], 0, "With no separation, the receiver cannot update.", "Do the types reveal anything?"),
         Q("Off the equilibrium path, which beliefs does PBE allow?", ["Any belief at all", "Only the prior", "Only certainty about a type", "None, it requires Bayes' rule"], 0, "Bayes' rule is undefined off the path, so PBE places no restriction.", "Why can't you apply Bayes' rule to a signal that never happens?")]),

    lvl("Beer-Quiche", "Fenwick the Fox", "marsh",
        [("E", "I'm the receiver. The sender is a Real Man (prefers Beer) or a Wimp (prefers Quiche). I fight a Wimp but avoid a Real Man. The sender mainly wants to avoid a fight.")],
        [lambda: Signal(BQ)],
        ["LESSON - THE BEER-QUICHE GAME: both types can pool on Beer or both pool on Quiche, supported by off-path beliefs. For example, pooling on Beer is sustained if, after seeing Quiche, the receiver believes the sender is probably a Wimp and fights. Multiple pooling strategies produce equilibria, and some off-path beliefs needed to sustain them are strange; later refinements tell us how to filter these out.",
         "LESSON - SEMI-SEPARATING (PARTIALLY POOLING) EQUILIBRIUM: one type plays a pure strategy while the other mixes, with one of its mixed actions equal to the first type's action. The signal is partly informative. These are the richest but hardest equilibria because they need many indifference conditions to sustain the mixing."],
        [Q("To sustain pooling on Beer, what must the receiver believe after Quiche?", ["The sender is probably a Wimp", "The sender is surely a Real Man", "The prior is entirely unchanged", "The sender is certainly lying"], 0, "Fighting after Quiche deters a Wimp from deviating from Beer.", "What belief makes a fight worthwhile after Quiche?"),
         Q("How many PBE do pooling situations usually have?", ['Often infinitely many', 'Exactly one in total', 'Exactly two in total', 'None at all, ever'], 0, "Off-path beliefs are free, so many belief choices work.", "Recall the lecture on off-the-path beliefs."),
         Q("In a semi-separating equilibrium, one type plays a pure strategy and the other...", ["mixes, including the first type's action", "plays a different pure strategy", "mixes between actions the first never uses", "does not move at all"], 0, "That overlap makes the signal partially informative.", "What does 'semi' mean here?")],
        info_extra("Nature draws Real Man or Wimp. The sender chooses Beer or Quiche. The receiver observes it and chooses Fight or Not.")),
]

FINAL_POOL = [
    Q("Deleting which kind of dominated strategy never loses an equilibrium?", ["Strictly dominated strategies", "Weakly dominated strategies", "Both kinds, in every game", "Neither kind, in any game"], 0, "Strictly dominated strategies are never part of an equilibrium; weakly dominated ones can be.", "Recall Pete's rope bridge."),
    Q("In a mixed Nash equilibrium, your probabilities are chosen to make...", ["the opponent indifferent", "your own payoffs equal", "the game zero-sum", "every cell equally likely"], 0, "Your mix comes from the OTHER player's payoffs.", "Recall Clara's pebbles."),
    Q("A subgame perfect equilibrium must specify...", ["an action at every decision node", "only the path of play", "only the first mover's choice", "only mixed strategies"], 0, "Off-path choices matter for credibility.", "Recall 'how NOT to write an SPE'."),
    Q("Grim trigger sustains cooperation when...", ["players are patient enough", "the last stage is known", "payoffs are exactly equal", "defections cannot be observed"], 0, "d must be at least 1/2 in the Prisoner's Dilemma used here.", "Recall the minimum d."),
    Q("A Bayesian Nash equilibrium requires...", ["a strategy for every type of every player", "a strategy for the average type only", "beliefs that ignore Nature's draw", "pure strategies from every player"], 0, "Every type must best-respond.", "Recall Harsanyi's trick."),
    Q("A perfect Bayesian equilibrium is made of...", ["strategies and beliefs updated by Bayes' rule", "strategies only, exactly as in Nash", "beliefs only, with no strategies at all", "payoffs and probabilities only, nothing more"], 0, "Beliefs must be written down and updated by Bayes' rule wherever possible.", "Recall the marsh levels."),
    Q("In a second price auction with private values, a good strategy is to...", ["bid exactly your true value", "shade your bid below your value", "inflate your bid above your value", "copy the average of other bids"], 0, "Your bid never sets your price, so honesty is best.", "Recall Gorg's auction."),
    Q("A risk averse person's utility function is...", ["concave, it bends downward", "convex, it bends upward", "linear, a straight line", "flat, never changing at all"], 0, "A sure amount beats a gamble with the same expected value.", "Recall the square root example."),
    Q("How many equilibria (pure and mixed) does the Stag Hunt have?", ["Three, by the odd rule", "Two, both of them pure", "Four, in two matching pairs", "One, since Stag dominates"], 0, "Two pure plus one mixed.", "Recall the odd rule."),
    Q("Tit-for-tat in the repeated Prisoner's Dilemma is...", ["almost never subgame perfect", "always subgame perfect", "never a Nash equilibrium", "equal to grim trigger exactly"], 0, "It holds only at a knife-edge discount factor.", "Recall Gorg the gorilla."),
    Q("In a pooling equilibrium, on-path beliefs equal...", ["the prior from Nature", "certainty about one type", "a random number each time", "the receiver's own payoff"], 0, "Nothing is learned from a signal everyone sends.", "Recall the marsh levels."),
    Q("Adverse selection happens when...", ["mostly low-quality sellers stay in", "every seller leaves the market", "buyers know each car's quality", "prices rise above every value"], 0, "At a price below the good sellers' reserve, only bad types sell.", "Recall the used car market."),
    Q("In the centipede game, backward induction predicts...", ["the first mover takes right away", "everyone passes until the end", "a random choice at each node", "the second mover decides everything"], 0, "Solving from the last node unravels cooperation.", "Recall Moe's banana pile."),
    Q("The winner's curse suggests you should bid...", ["below your raw estimate", "exactly at your raw estimate", "above your raw estimate", "at zero every time"], 0, "Winning tells you others estimated lower.", "Recall Bayes and the curse."),
]

REGION9 = [
    lvl("Final Exam", "Captain Nash", "dock",
        [("E", "Ahoy, survivor! I'm Captain Nash, the ferry captain. You've crossed all nine units, but to board you must defeat me in a quiz duel."),
         ("E", "Eight questions drawn from the whole course. Answer right and I take damage. Answer wrong and you lose a heart. You only have three hearts!")],
        [lambda: Boss("dock", "Final Exam - Duel with Captain Nash", FINAL_POOL, n=8)],
        None, None),
]
