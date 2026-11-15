"""Each level's title card shows 'Watch' buttons that open the matching Game Theory 101 lectures.
All lectures are by William Spaniel (gametheory101.com). Level name -> [(lecture title, slug)]."""
from sp_engine import LINKS

LINKS.update({
    # Unit 1: The Basics
    "Strict Dominance": [("The Prisoner's Dilemma and Strict Dominance", "the-prisoners-dilemma-and-strict-dominance")],
    "Eliminating": [("Iterated Elimination of Strictly Dominated Strategies", "itereated-elimination-of-strictly-dominated-strategies")],
    "Nash & Stag Hunt": [("Pure Strategy Nash Equilibrium and the Stag Hunt", "the-stag-hunt-and-pure-strategy-nash-equilibrium"),
                         ("What Is a Nash Equilibrium?", "what-is-a-nash-equilibrium"), ("Best Responses", "best-responses")],
    "Mixed Strategies": [("Matching Pennies and Mixed Strategy NE", "matching-pennies-and-mixed-strategy-nash-equilibrium"),
                         ("The Mixed Strategy Algorithm", "mixed-strategy-algorithm"),
                         ("How NOT to Write a Mixed Strategy NE", "how-not-to-write-a-mixed-strategy-nash-equilibrium")],
    "Battle of the Sexes": [("Battle of the Sexes", "battle-of-the-sexes"), ("Calculating Payoffs", "calculating-payoffs-of-mixed-strategy-nash-equilibria")],
    "Mixed Dominance": [("Strict Dominance in Mixed Strategies", "strict-dominance-in-mixed-strategies")],
    "Weak Dominance": [("Weak Dominance", "weak-dominance"), ("Infinitely Many Equilibria", "infinitely-many-equilibria")],
    "The Odd Rule": [("The Odd Rule", "odd-rule")],
    # Unit 2: Extensive Form
    "Backward Induction": [("Subgame Perfect Equilibrium", "subgame-perfect-equilibrium"), ("Backward Induction", "backward-induction")],
    "Writing SPE": [("How NOT to Write a Subgame Perfect Equilibrium", "how-not-to-write-a-subgame-perfect-equilibrium"),
                    ("Multiple Subgame Perfect Equilibria", "multiple-subgame-perfect-equilibria")],
    "Games w/ Stages": [("Games with Stages", "games-with-stages")],
    "Punishment": [("Punishment Strategies", "punishment-strategies")],
    "Tying Hands": [("Tying Hands (Burning Bridges)", "tying-hands-burning-bridges"),
                    ("Commitment Problems", "https://gametheory101.com/courses/international-relations-101/commitment-problems/")],
    "Centipede": [("The Centipede Game", "the-centipede-game"), ("Problems with Backward Induction", "problems-with-backward-induction"),
                  ("Forward Induction", "forward-induction")],
    # Unit 3: Advanced Strategic Form
    "Gen. Battle": [("Probability Distributions", "probability-distributions"), ("Generalized Battle of the Sexes", "generalized-battle-of-the-sexes")],
    "Penalty Kicks": [("Knife-Edge Equilibria", "knife-edge-equilibria"), ("Soccer Penalty Kicks", "soccer-penalty-kicks")],
    "Comp. Statics": [("Comparative Statics", "comparative-statics"), ("The Support of Mixed Strategies", "support-of-mixed-strategies")],
    "Weak Dom. Trick": [("A Trick with Weak Dominance", "a-trick-with-weak-dominance")],
    "Rock Paper Scissors": [("Rock Paper Scissors", "rock-paper-scissors"), ("Symmetric, Zero Sum Games", "symmetric-zero-sum-games")],
    "Modified RPS": [("Modified Rock Paper Scissors", "modified-rock-paper-scissors"), ("Mixing among Three Strategies", "mixing-among-three-strategies")],
    # Unit 4: Infinite Strategy Spaces
    "No Equilibria": [("A Game with No Equilibria", "a-game-with-no-equilibria"), ("Duels", "duels")],
    "Median Voter": [("Hotelling's Game and the Median Voter Theorem", "hotellings-game-and-the-median-voter-theorem")],
    "Second Price Auction": [("Second Price Auctions", "second-price-auction")],
    # Unit 5: Expected Utility
    "Preferences": [("Intro to Expected Utility Theory", "expected-utility-theory"), ("The Completeness Axiom", "the-completeness-axiom"),
                    ("The Transitivity Axiom", "the-transitivity-axiom"), ("Rationality", "rationality")],
    "Lotteries": [("Condorcet's Paradox", "condorcets-paradox-and-social-preferences"), ("Lotteries", "lotteries"),
                  ("Independence over Lotteries", "independence-over-lotteries"), ("The Allais Paradox", "the-allais-paradox")],
    "Utility & Risk": [("The Continuity Axiom", "the-continuity-axiom"), ("EU Transformations", "expected-utility-transformations"),
                       ("Pareto Efficiency", "pareto-efficiency"), ("Risk Attitudes", "risk-averse-risk-neutral-and-risk-acceptant-preferences")],
    # Unit 6: Repeated Games
    "Finite Repeats": [("Repeated Prisoner's Dilemma (Finite)", "repeated-prisoners-dilemma-finite")],
    "Discounting": [("Discount Factors", "discount-factors"), ("Geometric Series and Infinite Payoffs", "geometric-series-and-infinite-payoffs")],
    "Grim Trigger": [("The One-Shot Deviation Principle", "the-one-shot-deviation-principle"),
                     ("Grim Trigger in the Repeated PD", "grim-trigger-in-the-repeated-prisoners-dilemma")],
    "Tit-for-Tat": [("Tit-for-Tat in the Repeated PD", "tit-for-tat-in-the-repeated-prisoners-dilemma"),
                    ("Tit-for-Tat Isn't Subgame Perfect", "tit-for-tat-isnt-subgame-perfect")],
    "Folk Theorem": [("The Folk Theorem", "the-folk-theorem"), ("Repeated Games and the Prediction Problem", "repeated-games-and-the-prediction-problem")],
    # Unit 7: Bayesian Nash
    "Incomplete Info": [("Introduction to Incomplete Information", "introduction-to-incomplete-information"),
                        ("Bayesian Nash Equilibrium", "bayesian-nash-equilibrium"), ("Finding BNE with Nash Equilibrium", "solving-for-bayesian-nash-equilibrium")],
    "Dominance & Types": [("Ex Ante and Interim Dominance", "ex-ante-and-interim-dominance")],
    "Poker & Info": [("Why Are There Antes in Poker?", "why-are-there-antes-in-poker"), ("Is More Information Always Better?", "is-more-information-always-better")],
    "Cutpoints": [("Continuous Types and Cutpoint Strategies", "cutpoint-strategies-and-continuous-type-spaces"), ("The Purification Theorem", "the-purification-theorem")],
    "Bayes & Curse": [("Bayes' Rule", "bayes-rule"), ("The Winner's Curse", "the-winners-curse")],
    # Unit 8: Perfect Bayesian Equilibrium
    "PBE & Screening": [("Perfect Bayesian Equilibrium", "perfect-bayesian-equilibrium"), ("Screening Games", "screening-games"), ("Adverse Selection", "adverse-selection")],
    "Separating": [("Signaling Games and Updating Beliefs", "signaling-games"), ("Separating Equilibrium", "separating-equilibrium")],
    "Pooling": [("Pooling Equilibrium", "pooling-equilibrium"), ("Off-the-Path Beliefs", "off-the-path-beliefs")],
    "Beer-Quiche": [("The Beer-Quiche Game", "the-beer-quiche-game"), ("Semi-Separating Equilibrium", "semi-separating-partially-pooling-equilibrium")],
    # Finale
    "Final Exam": [("The whole course on YouTube", "https://www.youtube.com/playlist?list=PLKI1h_nAkaQoDzI4xDIXzx6U2ergFmedo")],
})
