# Search doesn't keep up with catalog edits

Merchandisers report that catalog search doesn't keep up with their edits.
Yesterday sku-2214 was renamed from "wireless earbuds" to "bluetooth earbuds";
an hour later it still matched "wireless" and not "bluetooth". Deleted items
sometimes keep surfacing in results too. Running `python -m catalog.cli
rebuild` clears it up, but the problem creeps back within a day, usually after
a busy editing session or a midday app restart. Nothing shows in the logs.
Expected: shortly after saving, an item matches
searches for its current name, description and tags, and deleted items stop
appearing. Actual: some items keep matching old wording or miss new wording.
