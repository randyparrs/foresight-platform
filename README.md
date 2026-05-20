# Foresight

An AI-powered prediction market platform where news articles become YES/NO markets and get resolved automatically through AI consensus. Built on GenLayer Studio testnet.

## What is this

Prediction markets work better when they are directly connected to the news that drives them. Most platforms treat market creation and resolution as separate problems handled by humans or centralized oracles. I built Foresight to explore whether both could be handled by an intelligent contract on GenLayer: the contract reads a real news URL, generates a binary market question, and resolves it using AI consensus without any admin deciding the outcome.

Users connect a wallet and bet YES or NO on any open market. When the market closes, the AI resolves it by fetching the source article and evaluating what actually happened. Winners claim points proportional to the pool. There is no human arbiter.

## Why GenLayer

The core problem with AI-resolved markets is trust. If a single AI decides whether an event happened, you have to trust that AI and whoever controls it. GenLayer solves this with Optimistic Democracy: multiple independent validator nodes each run the same AI evaluation, and the result is only committed on-chain when enough validators agree. A single validator cannot manipulate the outcome.

A traditional setup using a centralized backend could simulate this, but the results would be off-chain and modifiable. Here every market, every prediction, and every resolution is a transaction on GenLayer Studio testnet that anyone can verify.

## How it works

When the bot or a user calls generate_market with a news URL, the contract fetches the article, extracts the key claim, and stores a YES/NO question on-chain with a 50/50 starting split. Any wallet can call place_prediction to bet one point on either side. The pool adjusts with each new prediction and the probability updates accordingly.

When a market is ready to settle, anyone calls resolve_market which triggers Optimistic Democracy consensus. The leader node fetches the source URL and determines the outcome. Validators independently do the same and compare results. If enough validators agree, the market moves to RESOLVED and winners can claim their points. If validators cannot agree the market goes to DISPUTED and re_resolve_market can be called to try again.

The contract uses the Equivalence Principle for all non-deterministic operations. The leader performs the web fetch and AI reasoning first, then validators reproduce the same steps independently. This is what makes the AI resolution trustworthy instead of a single model call.

## Contract functions

**Markets contract — 0x705eF45c6dEC36dE0E8fF4c17E7e6E24CB6bB359**

generate_market takes a news URL and an optional terms string. The AI reads the article and generates a market question stored on-chain with OPEN status.

place_prediction takes a market ID and a side of YES or NO. Each prediction costs one point. Only open markets accept predictions.

resolve_market takes a market ID and triggers AI resolution through Optimistic Democracy. The market moves to RESOLVED with a result, or to DISPUTED if validators cannot agree.

re_resolve_market takes a market ID and retriggers resolution on a DISPUTED market. Can be called multiple times until consensus is reached.

expire_market takes a market ID and can only be called by the contract owner. Moves an OPEN market to EXPIRED, which entitles all predictors to a refund.

claim_winnings takes a market ID and transfers the proportional pool reward to the caller if they predicted correctly on a RESOLVED market.

claim_refund takes a market ID and returns the caller's stake on an EXPIRED market.

get_market takes a market ID and returns the full state including question, pool sizes, probability, status, result, and quality score.

get_summary returns global statistics including total markets, open count, resolved count, expired count, and total predictions placed.

get_top_predictors returns the ranked list of wallets by wins, losses, win rate, and net points.

get_my_predictions takes a wallet address and returns all prediction records for that wallet including market ID, side, and outcome.

get_markets_by_category takes a category string and returns all market IDs in that category. Valid categories are CRYPTO, TECH, POLITICS, SPORTS, and OTHER.

## Test results

Tested every contract function across multiple markets and wallets to confirm the full flow works end to end.

A market generated from a Wikipedia article about Ethereum resolved correctly on the first attempt and the winner claimed points from the pool without issues. CoinDesk URLs sometimes trigger a Vercel security checkpoint that blocks the AI web fetch, which causes the market to go DISPUTED. Wikipedia and similar open sources work reliably. When a market goes DISPUTED, calling re_resolve_market one or two more times is usually enough to reach consensus.

A POLITICS market about Federal Reserve rate decisions resolved correctly. An EXPIRED market was also tested by calling expire_market as owner, then claim_refund from a predictor wallet. Both worked as expected.

The view function get_market_count had a bug in early versions where calling int() on a u256 storage variable returned zero inside the GenLayer view execution context. This affected all counter-based loops. The fix was to scan the DynArray storage directly using len() and string pattern matching instead of relying on the counter. The contract was redeployed after this fix.

## How to run it

Go to GenLayer Studio at https://studio.genlayer.com and create a new file called Foresight_markets.py. Paste the contract code, deploy it, and note the contract address.

Follow this order and wait for FINALIZED at each step. Call get_summary first to confirm the contract is live. Call generate_market with any news URL and an empty string for terms. Call get_market with ID 0 to confirm the market was stored. Call place_prediction with market ID 0 and a side of YES or NO. Call resolve_market with market ID 0. Wait for FINALIZED, then call get_market again to see the result. If it shows RESOLVED and your side matches the result, call claim_winnings. If the market shows DISPUTED, call re_resolve_market and wait for FINALIZED again.

Use Wikipedia URLs or similar open sources for reliable results. Commercial news sites with paywalls or bot detection will cause DISPUTED outcomes.

## The bot

An off-chain bot automates platform activity so markets and articles are generated continuously without manual intervention. The bot runs on a GitHub Actions cron job triggered every 30 minutes via cron-job.org. Each run picks a random news article from a curated pool, calls generate_market on the Markets contract, and calls publish_article on The Signal contract. The bot uses genlayer-js to send transactions and waits for each one to reach FINALIZED status before exiting.

The bot repository is at https://github.com/randyparrs/foresight-bot and the private key is stored as a GitHub Actions secret.

## Live frontend

The frontend is deployed at https://foresightmrkts.netlify.app and connects directly to the contracts on GenLayer Studio testnet using a custom client built on genlayer-js.

The home page shows a live ticker of all open markets, real-time stats from the contract, the most recent markets as clickable cards, and the most recent Signal articles. The markets page shows all on-chain markets with YES/NO probability bars, pool sizes, and category filters. Each card has betting buttons for open markets and action buttons for resolved, disputed, and expired states. The leaderboard shows the top predictors ranked by net points and win rate pulled live from get_top_predictors. If your wallet is connected and you appear in the ranking, a YOUR POSITION card shows your stats at the top. The notification bell loads your prediction history on wallet connect and shows a WIN, LOSS, or REFUND notification for every settled market you participated in.

## The Signal

The Signal is a second intelligent contract deployed alongside Foresight. It is an on-chain AI journalist called SIG-01 that reads real news URLs, writes a three-paragraph factual article, assigns sentiment, and publishes it on-chain after independent validators agree on the content. Articles are permanent, queryable by category and block number, and visible on the Signal page of the frontend. The bot publishes one new article every 30 minutes alongside each new market. Contract address is 0x46e821C8Ec4D329AEd82F9e4FB4D9AcEBD573F17.

## Resources

GenLayer Docs at https://docs.genlayer.com

Optimistic Democracy at https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy

Equivalence Principle at https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle

GenLayer Studio at https://studio.genlayer.com

Discord at https://discord.gg/8Jm4v89VAu
