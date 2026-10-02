import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

type DemoVerification = {
  applicationId: string;
  personName: string;
  status: "VERIFIED" | "REVIEW_REQUIRED" | "REJECTED";
  reason: string;
};

const demoVerifications: DemoVerification[] = [
  {
    applicationId: "demo-app-ava",
    personName: "Ava Schneider",
    status: "VERIFIED",
    reason: "Demo document fields matched and document is not expired."
  },
  {
    applicationId: "demo-app-noah",
    personName: "Noah Weber",
    status: "REVIEW_REQUIRED",
    reason: "OCR did not match the expected document number."
  },
  {
    applicationId: "demo-app-mia",
    personName: "Mia Fischer",
    status: "REJECTED",
    reason: "Document is expired."
  }
];

const server = new McpServer({
  name: "identity-demo-mcp",
  version: "1.0.0"
});

server.registerTool(
  "get_demo_verification",
  {
    title: "Get a fictional verification record",
    description:
      "Returns a fictional, read-only verification result for demo purposes. It does not access real customer data.",
    inputSchema: z.object({
      applicationId: z.string().describe("Fictional demo application ID")
    })
  },
  async ({ applicationId }) => {
    const result = demoVerifications.find(
      (record) => record.applicationId === applicationId
    );

    if (!result) {
      return {
        content: [
          {
            type: "text" as const,
            text: `No fictional demo record exists for applicationId=${applicationId}.`
          }
        ],
        isError: true
      };
    }

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }
);

server.registerTool(
  "list_demo_verification_statistics",
  {
    title: "List fictional verification statistics",
    description: "Returns aggregate status counts from fictional demo records.",
    inputSchema: z.object({})
  },
  async () => {
    const counts = demoVerifications.reduce<Record<string, number>>(
      (acc, item) => {
        acc[item.status] = (acc[item.status] ?? 0) + 1;
        return acc;
      },
      {}
    );

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              scope: "fictional demo records only",
              counts
            },
            null,
            2
          )
        }
      ]
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);