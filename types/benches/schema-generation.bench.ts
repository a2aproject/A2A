import { resolve } from "path";
import { bench, describe } from "vitest";
import * as TJS from "typescript-json-schema";

const typesFile = resolve(__dirname, "../src/types.ts");

const compilerOptions: TJS.CompilerOptions = {
  strictNullChecks: false,
  skipLibCheck: true,
};

describe("JSON Schema Generation", () => {
  bench("generate full schema from types.ts", () => {
    const program = TJS.getProgramFromFiles([typesFile], compilerOptions);
    TJS.generateSchema(program, "*", {
      required: true,
      defaultNumberType: "integer",
    });
  });

  bench("build schema generator", () => {
    const program = TJS.getProgramFromFiles([typesFile], compilerOptions);
    TJS.buildGenerator(program, {
      required: true,
      defaultNumberType: "integer",
    });
  });

  bench("generate schema for AgentCard type", () => {
    const program = TJS.getProgramFromFiles([typesFile], compilerOptions);
    TJS.generateSchema(program, "AgentCard", {
      required: true,
      defaultNumberType: "integer",
    });
  });

  bench("generate schema for Task type", () => {
    const program = TJS.getProgramFromFiles([typesFile], compilerOptions);
    TJS.generateSchema(program, "Task", {
      required: true,
      defaultNumberType: "integer",
    });
  });

  bench("generate schema for Message type", () => {
    const program = TJS.getProgramFromFiles([typesFile], compilerOptions);
    TJS.generateSchema(program, "Message", {
      required: true,
      defaultNumberType: "integer",
    });
  });
});
