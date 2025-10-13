import type * as grpc from '@grpc/grpc-js';
import type { EnumTypeDefinition, MessageTypeDefinition } from '@grpc/proto-loader';

import type { A2AServiceClient as _a2a_v1_A2AServiceClient, A2AServiceDefinition as _a2a_v1_A2AServiceDefinition } from './a2a/v1/A2AService';

type SubtypeConstructor<Constructor extends new (...args: any) => any, Subtype> = {
  new(...args: ConstructorParameters<Constructor>): Subtype;
};

export interface ProtoGrpcType {
  a2a: {
    v1: {
      /**
       * A2AService defines the gRPC version of the A2A protocol. This has a slightly
       * different shape than the JSONRPC version to better conform to AIP-127,
       * where appropriate. The nouns are AgentCard, Message, Task and
       * TaskPushNotificationConfig.
       * - Messages are not a standard resource so there is no get/delete/update/list
       * interface, only a send and stream custom methods.
       * - Tasks have a get interface and custom cancel and subscribe methods.
       * - TaskPushNotificationConfig are a resource whose parent is a task.
       * They have get, list and create methods.
       * - AgentCard is a static resource with only a get method.
       */
      A2AService: SubtypeConstructor<typeof grpc.Client, _a2a_v1_A2AServiceClient> & { service: _a2a_v1_A2AServiceDefinition }
      APIKeySecurityScheme: MessageTypeDefinition
      AgentCapabilities: MessageTypeDefinition
      AgentCard: MessageTypeDefinition
      AgentCardSignature: MessageTypeDefinition
      AgentExtension: MessageTypeDefinition
      AgentInterface: MessageTypeDefinition
      AgentProvider: MessageTypeDefinition
      AgentSkill: MessageTypeDefinition
      Artifact: MessageTypeDefinition
      AuthenticationInfo: MessageTypeDefinition
      AuthorizationCodeOAuthFlow: MessageTypeDefinition
      CancelTaskRequest: MessageTypeDefinition
      ClientCredentialsOAuthFlow: MessageTypeDefinition
      CreateTaskPushNotificationConfigRequest: MessageTypeDefinition
      DataPart: MessageTypeDefinition
      DeleteTaskPushNotificationConfigRequest: MessageTypeDefinition
      FilePart: MessageTypeDefinition
      GetAgentCardRequest: MessageTypeDefinition
      GetTaskPushNotificationConfigRequest: MessageTypeDefinition
      GetTaskRequest: MessageTypeDefinition
      HTTPAuthSecurityScheme: MessageTypeDefinition
      ImplicitOAuthFlow: MessageTypeDefinition
      ListTaskPushNotificationConfigRequest: MessageTypeDefinition
      ListTaskPushNotificationConfigResponse: MessageTypeDefinition
      Message: MessageTypeDefinition
      MutualTlsSecurityScheme: MessageTypeDefinition
      OAuth2SecurityScheme: MessageTypeDefinition
      OAuthFlows: MessageTypeDefinition
      OpenIdConnectSecurityScheme: MessageTypeDefinition
      Part: MessageTypeDefinition
      PasswordOAuthFlow: MessageTypeDefinition
      PushNotificationConfig: MessageTypeDefinition
      Role: EnumTypeDefinition
      Security: MessageTypeDefinition
      SecurityScheme: MessageTypeDefinition
      SendMessageConfiguration: MessageTypeDefinition
      SendMessageRequest: MessageTypeDefinition
      SendMessageResponse: MessageTypeDefinition
      StreamResponse: MessageTypeDefinition
      StringList: MessageTypeDefinition
      Task: MessageTypeDefinition
      TaskArtifactUpdateEvent: MessageTypeDefinition
      TaskPushNotificationConfig: MessageTypeDefinition
      TaskState: EnumTypeDefinition
      TaskStatus: MessageTypeDefinition
      TaskStatusUpdateEvent: MessageTypeDefinition
      TaskSubscriptionRequest: MessageTypeDefinition
    }
  }
  google: {
    api: {
      ClientLibraryDestination: EnumTypeDefinition
      ClientLibraryOrganization: EnumTypeDefinition
      ClientLibrarySettings: MessageTypeDefinition
      CommonLanguageSettings: MessageTypeDefinition
      CppSettings: MessageTypeDefinition
      CustomHttpPattern: MessageTypeDefinition
      DotnetSettings: MessageTypeDefinition
      FieldBehavior: EnumTypeDefinition
      GoSettings: MessageTypeDefinition
      Http: MessageTypeDefinition
      HttpRule: MessageTypeDefinition
      JavaSettings: MessageTypeDefinition
      LaunchStage: EnumTypeDefinition
      MethodSettings: MessageTypeDefinition
      NodeSettings: MessageTypeDefinition
      PhpSettings: MessageTypeDefinition
      Publishing: MessageTypeDefinition
      PythonSettings: MessageTypeDefinition
      RubySettings: MessageTypeDefinition
    }
    protobuf: {
      DescriptorProto: MessageTypeDefinition
      Duration: MessageTypeDefinition
      Edition: EnumTypeDefinition
      Empty: MessageTypeDefinition
      EnumDescriptorProto: MessageTypeDefinition
      EnumOptions: MessageTypeDefinition
      EnumValueDescriptorProto: MessageTypeDefinition
      EnumValueOptions: MessageTypeDefinition
      ExtensionRangeOptions: MessageTypeDefinition
      FeatureSet: MessageTypeDefinition
      FeatureSetDefaults: MessageTypeDefinition
      FieldDescriptorProto: MessageTypeDefinition
      FieldOptions: MessageTypeDefinition
      FileDescriptorProto: MessageTypeDefinition
      FileDescriptorSet: MessageTypeDefinition
      FileOptions: MessageTypeDefinition
      GeneratedCodeInfo: MessageTypeDefinition
      ListValue: MessageTypeDefinition
      MessageOptions: MessageTypeDefinition
      MethodDescriptorProto: MessageTypeDefinition
      MethodOptions: MessageTypeDefinition
      NullValue: EnumTypeDefinition
      OneofDescriptorProto: MessageTypeDefinition
      OneofOptions: MessageTypeDefinition
      ServiceDescriptorProto: MessageTypeDefinition
      ServiceOptions: MessageTypeDefinition
      SourceCodeInfo: MessageTypeDefinition
      Struct: MessageTypeDefinition
      SymbolVisibility: EnumTypeDefinition
      Timestamp: MessageTypeDefinition
      UninterpretedOption: MessageTypeDefinition
      Value: MessageTypeDefinition
    }
  }
}

