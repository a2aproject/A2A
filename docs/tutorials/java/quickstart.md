# Java Quickstart: Build and Call an A2A Agent

In this tutorial, you will build a local A2A server with Quarkus and call it from a Java client. The agent always replies with `Hello World`, so you do not need an LLM, an API key, or an external service.

You will learn how an `AgentSkill` describes an agent's capabilities, how an `AgentCard` advertises its endpoint, and how an `AgentExecutor` handles a message. The example uses JSON-RPC and a non-streaming response to keep the first interaction simple.

## 1. Set Up Your Environment

You need:

- JDK 17 or later, with `JAVA_HOME` pointing to that JDK.
- Maven 3.9 or later.
- Internet access to download Maven dependencies. Once built, the interaction uses only the local server.

Check your tools:

```sh
java -version
mvn -version
```

This tutorial pins the A2A Java SDK to `1.4.0.Final` and Quarkus to `3.39.2`, matching the SDK release's Quarkus version. The SDK implements A2A 1.0; do not mix this code with older examples that import `io.a2a.*` or advertise an Agent Card using `url` and `preferredTransport`.

Create a directory named `a2a-java-quickstart` with separate server and client projects:

=== "Linux/macOS"

    ```sh
    mkdir a2a-java-quickstart
    cd a2a-java-quickstart
    mkdir -p server/src/main/java/example server/src/main/resources client/src/main/java/example
    ```

=== "Windows (PowerShell)"

    ```powershell
    New-Item -ItemType Directory a2a-java-quickstart
    Set-Location a2a-java-quickstart
    New-Item -ItemType Directory -Force -Path server/src/main/java/example, server/src/main/resources, client/src/main/java/example
    ```

Keep this directory as your working directory unless a step says otherwise. Create the files below in your editor.

## 2. Configure the Server

Create `server/pom.xml`:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>example</groupId>
    <artifactId>a2a-quickstart-server</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>17</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <quarkus.platform.version>3.39.2</quarkus.platform.version>
        <a2a.version>1.4.0.Final</a2a.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>io.quarkus.platform</groupId>
                <artifactId>quarkus-bom</artifactId>
                <version>${quarkus.platform.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.a2aproject.sdk</groupId>
            <artifactId>a2a-java-sdk-reference-jsonrpc</artifactId>
            <version>${a2a.version}</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.1</version>
            </plugin>
            <plugin>
                <groupId>io.quarkus.platform</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${quarkus.platform.version}</version>
                <extensions>true</extensions>
                <executions>
                    <execution>
                        <goals>
                            <goal>build</goal>
                            <goal>generate-code</goal>
                            <goal>generate-code-tests</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

The reference server supplies the JSON-RPC transport and Quarkus integration. You provide the agent's description and execution logic as CDI beans; you do not need to write an HTTP controller.

Create `server/src/main/resources/application.properties`:

```properties
quarkus.http.host=127.0.0.1
quarkus.http.port=9999
a2a.authorization.required=false
```

!!! warning "Local development only"

    This example disables task authorization and has no authentication configuration. It binds to the loopback interface so it is reachable only from your machine. Before exposing an agent remotely, configure authentication and authorization as described in the [Java SDK security guide](https://a2aproject.github.io/a2a-java/1_4_0_Final/security/).

## 3. Define an Agent Skill and Agent Card

An `AgentSkill` describes an ability; it does not implement that ability. An `AgentCard` describes the agent, its skills, supported transports, and capabilities so a client can discover how to call it.

Create `server/src/main/java/example/AgentCardProducer.java`:

```java
package example;

import java.util.List;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;

import org.a2aproject.sdk.server.PublicAgentCard;
import org.a2aproject.sdk.spec.AgentCapabilities;
import org.a2aproject.sdk.spec.AgentCard;
import org.a2aproject.sdk.spec.AgentInterface;
import org.a2aproject.sdk.spec.AgentSkill;
import org.a2aproject.sdk.spec.TransportProtocol;

@ApplicationScoped
public class AgentCardProducer {

    @Produces
    @PublicAgentCard
    public AgentCard agentCard() {
        AgentSkill skill = AgentSkill.builder()
                .id("hello_world")
                .name("Say hello")
                .description("Returns a fixed greeting")
                .tags(List.of("greeting"))
                .examples(List.of("Say hello"))
                .build();

        return AgentCard.builder()
                .name("Hello World Agent")
                .description("A local Java A2A quickstart agent")
                .version("1.0.0")
                .supportedInterfaces(List.of(new AgentInterface(
                        TransportProtocol.JSONRPC.asString(),
                        "http://127.0.0.1:9999")))
                .capabilities(AgentCapabilities.builder()
                        .streaming(false)
                        .pushNotifications(false)
                        .build())
                .defaultInputModes(List.of("text"))
                .defaultOutputModes(List.of("text"))
                .skills(List.of(skill))
                .build();
    }
}
```

`@Produces` makes the card available through CDI, and `@PublicAgentCard` exposes it at `/.well-known/agent-card.json`. The advertised URL must match the server's host and port. The card's version describes this agent, not the SDK version.

The card deliberately advertises neither streaming nor push notifications: those capabilities are outside this first example.

## 4. Implement the Agent Executor

Create `server/src/main/java/example/AgentExecutorProducer.java`:

```java
package example;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;

import org.a2aproject.sdk.server.agentexecution.AgentExecutor;
import org.a2aproject.sdk.server.agentexecution.RequestContext;
import org.a2aproject.sdk.server.tasks.AgentEmitter;
import org.a2aproject.sdk.spec.A2AError;
import org.a2aproject.sdk.spec.UnsupportedOperationError;

@ApplicationScoped
public class AgentExecutorProducer {

    @Produces
    public AgentExecutor agentExecutor() {
        return new AgentExecutor() {
            @Override
            public void execute(RequestContext context, AgentEmitter emitter)
                    throws A2AError {
                emitter.sendMessage("Hello World");
            }

            @Override
            public void cancel(RequestContext context, AgentEmitter emitter)
                    throws A2AError {
                throw new UnsupportedOperationError();
            }
        };
    }
}
```

The reference server dispatches an incoming message to `execute`. `RequestContext` gives the executor access to the request, while `AgentEmitter` sends the response through the SDK.

This executor returns a `Message` directly. A2A also supports stateful `Task` responses, artifacts, and status updates, but they are not necessary for an immediate greeting. Because this example creates no long-running task, it does not implement cancellation.

## 5. Build and Start the Server

From `a2a-java-quickstart`, build the server:

```sh
mvn -f server/pom.xml package
```

Start the packaged application and leave it running:

```sh
java -jar server/target/quarkus-app/quarkus-run.jar
```

The startup log should include `Listening on: http://127.0.0.1:9999`. Open <http://127.0.0.1:9999/.well-known/agent-card.json> in a browser to inspect the card. You should see the agent's name, the `hello_world` skill, and a JSON-RPC interface pointing to `http://127.0.0.1:9999`.

If the port is already in use, stop the other application or choose another port. If you change it, update both `application.properties` and the Agent Card URL, as well as the client URL below.

## 6. Create a Java Client

Open a second terminal in `a2a-java-quickstart`.

Create `client/pom.xml`:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>example</groupId>
    <artifactId>a2a-quickstart-client</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>17</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.a2aproject.sdk</groupId>
            <artifactId>a2a-java-sdk-client</artifactId>
            <version>1.4.0.Final</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.1</version>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.6.3</version>
                <configuration>
                    <mainClass>example.HelloWorldClient</mainClass>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

Create `client/src/main/java/example/HelloWorldClient.java`:

```java
package example;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

import org.a2aproject.sdk.A2A;
import org.a2aproject.sdk.client.Client;
import org.a2aproject.sdk.client.MessageEvent;
import org.a2aproject.sdk.client.config.ClientConfig;
import org.a2aproject.sdk.client.http.A2ACardResolver;
import org.a2aproject.sdk.client.transport.jsonrpc.JSONRPCTransport;
import org.a2aproject.sdk.client.transport.jsonrpc.JSONRPCTransportConfig;
import org.a2aproject.sdk.spec.AgentCard;
import org.a2aproject.sdk.spec.Part;
import org.a2aproject.sdk.spec.TextPart;

public class HelloWorldClient {

    public static void main(String[] args) throws Exception {
        AgentCard card = A2ACardResolver.builder()
                .baseUrl("http://127.0.0.1:9999")
                .build()
                .getAgentCard();
        System.out.println("Discovered: " + card.name());

        CompletableFuture<String> response = new CompletableFuture<>();
        try (Client client = Client.builder(card)
                .clientConfig(new ClientConfig.Builder().setStreaming(false).build())
                .withTransport(JSONRPCTransport.class, new JSONRPCTransportConfig())
                .addConsumer((event, agentCard) -> {
                    if (event instanceof MessageEvent messageEvent) {
                        StringBuilder text = new StringBuilder();
                        for (Part<?> part : messageEvent.getMessage().parts()) {
                            if (part instanceof TextPart textPart) {
                                text.append(textPart.text());
                            }
                        }
                        response.complete(text.toString());
                    }
                })
                .streamingErrorHandler(response::completeExceptionally)
                .build()) {
            client.sendMessage(A2A.toUserMessage("Say hello"));
            String text = response.get(10, TimeUnit.SECONDS);
            if (!"Hello World".equals(text)) {
                throw new IllegalStateException("Unexpected response: " + text);
            }
            System.out.println("Response: " + text);
        }
    }
}
```

`A2ACardResolver` discovers the card from the well-known endpoint. The client then selects JSON-RPC, sends a user message, and delivers the agent's response to the registered consumer as a `MessageEvent`. The example checks the greeting rather than treating any response as success. The try-with-resources block closes the client when it finishes or fails.

The client explicitly disables streaming. Its consumer runs as part of the non-streaming message exchange; the future also bounds the wait for the expected event after `sendMessage` returns. It is not an overall HTTP request timeout.

## 7. Run and Verify the Interaction

With the server still running in the first terminal, run this command in the second:

```sh
mvn -f client/pom.xml compile exec:java
```

Alongside Maven's build output, you should see:

```console
Discovered: Hello World Agent
Response: Hello World
```

The execution path is: discover the card, send a JSON-RPC message, execute the agent, emit the reply, and handle the `MessageEvent` in the client. No model is involved: this verifies that discovery and the client/server protocol plumbing work before you add agent logic.

If discovery fails with a connection error, check that the server is running on port `9999`. If discovery returns 404, check that the card producer has `@PublicAgentCard`. If the client rejects the response, verify that your executor returns the exact greeting from this tutorial.

Stop the server with Ctrl+C when you are done.

## Next Steps

- Read the [Java SDK server guide](https://a2aproject.github.io/a2a-java/1_4_0_Final/server/) and [client guide](https://a2aproject.github.io/a2a-java/1_4_0_Final/client/) for task-based responses, streaming, and other transports.
- Explore the [Java SDK Hello World example](https://github.com/a2aproject/a2a-java/tree/v1.4.0.Final/examples/helloworld) for a fuller client/server example.
- Review the [life of an A2A task](../../topics/life-of-a-task.md) before implementing long-running work, cancellation, or multi-turn interactions.
- Browse the [Java agent samples](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents) when you are ready to replace the fixed greeting with model or tool calls.
