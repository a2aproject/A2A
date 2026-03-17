import { readFileSync } from "fs";
import { resolve } from "path";
import { bench, describe } from "vitest";

const schemaPath = resolve(__dirname, "../../specification/json/a2a.json");
const schemaContent = readFileSync(schemaPath, "utf-8");

describe("JSON Schema Operations", () => {
  bench("parse A2A JSON schema", () => {
    JSON.parse(schemaContent);
  });

  bench("parse and extract definitions", () => {
    const schema = JSON.parse(schemaContent);
    Object.keys(schema.definitions);
  });

  bench("serialize A2A JSON schema", () => {
    const schema = JSON.parse(schemaContent);
    JSON.stringify(schema);
  });

  bench("deep clone A2A JSON schema", () => {
    const schema = JSON.parse(schemaContent);
    JSON.parse(JSON.stringify(schema));
  });

  bench("resolve AgentCard type references", () => {
    const schema = JSON.parse(schemaContent);
    const definitions = schema.definitions;
    const agentCard = definitions["AgentCard"];
    if (agentCard && agentCard.properties) {
      for (const [, prop] of Object.entries(agentCard.properties)) {
        const p = prop as Record<string, unknown>;
        if (p["$ref"] && typeof p["$ref"] === "string") {
          const refName = (p["$ref"] as string).replace("#/definitions/", "");
          definitions[refName];
        }
      }
    }
  });
});
