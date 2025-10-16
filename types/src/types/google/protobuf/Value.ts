// Original file: null

import type {
  NullValue as _google_protobuf_NullValue,
  NullValue__Output as _google_protobuf_NullValue__Output,
} from "../../google/protobuf/NullValue";
import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";
import type {
  ListValue as _google_protobuf_ListValue,
  ListValue__Output as _google_protobuf_ListValue__Output,
} from "../../google/protobuf/ListValue";

export interface Value {
  nullValue?: _google_protobuf_NullValue;
  numberValue?: number | string;
  stringValue?: string;
  boolValue?: boolean;
  structValue?: _google_protobuf_Struct | null;
  listValue?: _google_protobuf_ListValue | null;
  kind?:
    | "nullValue"
    | "numberValue"
    | "stringValue"
    | "boolValue"
    | "structValue"
    | "listValue";
}

export interface Value__Output {
  nullValue?: _google_protobuf_NullValue__Output;
  numberValue?: number;
  stringValue?: string;
  boolValue?: boolean;
  structValue?: _google_protobuf_Struct__Output | null;
  listValue?: _google_protobuf_ListValue__Output | null;
  kind?:
    | "nullValue"
    | "numberValue"
    | "stringValue"
    | "boolValue"
    | "structValue"
    | "listValue";
}
