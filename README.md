![l](https://imgur.com/nMiqX4V.png)
# Mangalerts
## *IMPORTANT UPDATE* 
Mangalerts has shutdown indefinitely, with no plans to bring this bot back online any time soon. I encourage all with the ability to fork this project and improve it, Thanks for all the support! o7
----
Mangalerts is a discord bot that provides users with direct message notifications whenever a new chapter of their favorite manga title is released! By [addding Mangalerts to your discord server](https://discord.com/api/oauth2/authorize?client_id=852814525886758922&permissions=0&scope=bot), users can rest assured that they won't miss a single release of their chosen manga titles. Mangalerts runs using a cloudbased MongoDB database and pymongo, as well as the public [MangaDex API](https://api.mangadex.org/docs.html) and [MangaUpdates](https://www.mangaupdates.com/index.html) rss feed using [feedparser](https://pythonhosted.org/feedparser/index.html). MyAnimeList integration and anime release notifications coming soon!
## Adding Mangalerts to your server
Adding Mangalerts to your server is simple as clicking [here](https://discord.com/api/oauth2/authorize?client_id=852814525886758922&permissions=377957173248&scope=bot)!
## Usage
Like most other discord bots, manga alerts runs by typing in any whitelisted channel m![`command`] \<`args`>\, in which command is the name of the `command` and `args` is what is to be passed in as seen below. Do *not* attempt to use Mangalerts commands in a DM, as it will reply but not update the database.
|Command|Description|
| -------|----------- |
| m!track_manga [title] | Add manga title to personal tracking list. |
| m!untrack_manga [title]| Remove manga from personal tracking list. |
| m!untrack_all_manga| Remove all manga from personal tracking list. |
| m!my_manga| Returns a list of your tracked manga. |
| m!manga [title] | Returns a description and image of a manga title. |
| m!ping| Ping Mangalerts |
| m!help| Returns a list of commands and links |

### Examples
![alert](https://i.imgur.com/LRO6RgT.png) ![mymanga](https://i.imgur.com/zX3iyat.png) ![manga](https://i.imgur.com/mcohc3e.png)

## Still Have an Issue?
Contact me at mangalerts@gmail.com, or raise an issue on github.
