require("dotenv").config();
const fs = require("fs");
const path = require("path");
const { Client, RichPresence } = require("discord.js-selfbot-v13");
const figlet = require("figlet");

/* ---------------- PATCH PARA EVITAR CRASH EN RAILWAY ---------------- */
try {
    const patchPath = path.join(__dirname, "node_modules", "discord.js-selfbot-v13", "src", "managers", "ClientUserSettingManager.js");
    let content = fs.readFileSync(patchPath, "utf8");

    content = content.replace(
        "all: data.friend_source_flags.all || false,",
        "all: (data.friend_source_flags ? data.friend_source_flags.all : false),"
    );

    fs.writeFileSync(patchPath, content, "utf8");
    console.log("Selfbot patched successfully.");
} catch (e) {
    console.log("Patch skipped:", e.message);
}

/* ---------------- CONFIG ---------------- */
const CONFIG = {
    TOKEN: process.env.TOKEN,
    PREFIX: ".",
    BUTTONS: {
        gunslol: "https://guns.lol/colddavi.555",
        d3mxn: "https://discord.gg/gyhFNxtBRy"
    },
    STATUS_MESSAGES: [
        "dm for spam bot",
        "#d3mxn on top",
        "h3xo best nuke bot",
        "$$$"
    ],
    CHANGE_INTERVAL: 5000,
    AUTO_REACT_EMOJI: "❤️",
    LARGE_IMAGE: "",
    EIGHTBALL: [
        "yes", "no", "maybe", "definitely", "ask later", "don't count on it",
        "sure", "never", "probably", "idk"
    ]
};

/* ---------------- CLIENT ---------------- */
const client = new Client();
let currentStatusIndex = 0;
let lastDeleted = {};

/* ---------------- RPC ---------------- */
function setRichPresence(customText) {
    const status = customText || CONFIG.STATUS_MESSAGES[currentStatusIndex];

    try {
        const rpc = new RichPresence(client)
            .setApplicationId("1108131011735085196")
            .setType("STREAMING")
            .setURL("https://twitch.tv/dk3")
            .setName("nxg is here")
            .setDetails(status)
            .setState("active")
            .setStartTimestamp(Date.now())
            .addButton("gunslol", CONFIG.BUTTONS.gunslol)
            .addButton("d3mxn", CONFIG.BUTTONS.d3mxn);

        client.user.setPresence({
            activities: [rpc],
            status: "dnd"
        });

        console.log("Status updated: " + status);
    } catch (e) {
        console.log("RPC error: " + e.message);
    }

    if (!customText) {
        currentStatusIndex = (currentStatusIndex + 1) % CONFIG.STATUS_MESSAGES.length;
    }
}

/* ---------------- READY ---------------- */
client.on("ready", () => {
    console.log("Selfbot activated: " + client.user.tag);

    setTimeout(() => {
        setRichPresence();
        console.log("Rich Presence ON");

        setInterval(() => {
            setRichPresence();
        }, CONFIG.CHANGE_INTERVAL);
    }, 2000);
});

/* ---------------- SNIPE ---------------- */
client.on("messageDelete", message => {
    if (message.partial) return;
    lastDeleted[message.channel.id] = {
        content: message.content,
        author: message.author ? message.author.tag : "unknown",
        timestamp: message.createdTimestamp
    };
});

/* ---------------- COMMANDS ---------------- */
client.on("messageCreate", async message => {

    if (message.author.id === client.user.id) {
        try { await message.react(CONFIG.AUTO_REACT_EMOJI); } catch {}
    }

    if (message.author.id !== client.user.id) return;
    if (!message.content.startsWith(CONFIG.PREFIX)) return;

    const args = message.content.slice(CONFIG.PREFIX.length).trim().split(/ +/);
    const cmd = args.shift().toLowerCase();

    if (cmd === "ping") {
        message.reply("pong " + Math.round(client.ws.ping) + "ms");
    }

    if (cmd === "userinfo") {
        message.reply(
            "id: " + client.user.id +
            "\ntag: " + client.user.tag
        );
    }

    if (cmd === "serverinfo") {
        if (!message.guild) return message.reply("use in server");
        message.reply(
            "id: " + message.guild.id +
            "\nmembers: " + message.guild.memberCount
        );
    }

    if (cmd === "purge") {
        const n = parseInt(args[0]);
        if (!n || n < 1 || n > 100) return message.reply("use .purge 1-100");

        try {
            const msgs = await message.channel.messages.fetch({ limit: 100 });
            const mine = msgs.filter(m => m.author.id === client.user.id).first(n);

            for (const m of mine) await m.delete();

            const msg = await message.channel.send(mine.length + " messages deleted");
            setTimeout(() => msg.delete(), 3000);
        } catch {
            message.reply("error deleting");
        }
    }

    if (cmd === "setstatus") {
        const t = args.join(" ");
        if (!t) return message.reply("write status");
        setRichPresence(t);
        message.reply("status changed");
    }

    if (cmd === "coinflip") {
        message.reply(Math.random() < 0.5 ? "heads" : "tails");
    }

    if (cmd === "8ball") {
        if (!args.length) return message.reply("ask something");
        const r = CONFIG.EIGHTBALL[Math.floor(Math.random() * CONFIG.EIGHTBALL.length)];
        message.reply(r);
    }

    if (cmd === "roll") {
        const max = parseInt(args[0]) || 6;
        const r = Math.floor(Math.random() * max) + 1;
        message.reply("result: " + r + " (1-" + max + ")");
    }

    if (cmd === "spam") {
        const amount = parseInt(args.pop());
        const text = args.join(" ");

        if (!text || isNaN(amount) || amount < 1 || amount > 15)
            return message.reply("use .spam <text> <1-15>");

        for (let i = 0; i < amount; i++) {
            await message.channel.send(text);
            await new Promise(r => setTimeout(r, 300));
        }
    }

    if (cmd === "snipe") {
        const s = lastDeleted[message.channel.id];
        if (!s) return message.reply("nothing to snipe");
        message.reply(s.content || "(empty)");
    }

    if (cmd === "ascii") {
        const t = args.join(" ");
        if (!t) return message.reply("write text");

        figlet(t, (err, data) => {
            if (err || !data) return message.reply("ascii error");
            message.reply("```" + data.slice(0, 1900) + "```");
        });
    }

    if (cmd === "bio") {
        const t = args.join(" ");
        if (!t) return message.reply("usage: .bio <text>");

        try {
            await client.user.edit({ bio: t });
            message.reply("bio updated");
        } catch {
            message.reply("error updating bio");
        }
    }

    if (cmd === "help") {
        message.reply(
            "Commands:\n" +
            ".ping\n.userinfo\n.serverinfo\n.purge\n.bio\n.setstatus\n.coinflip\n.8ball\n.roll\n.spam\n.snipe\n.ascii\n.help"
        );
    }
});

/* ---------------- ERRORS ---------------- */
client.on("error", e => console.log("client error: " + e));

console.log("Starting selfbot...");
client.login(CONFIG.TOKEN);
