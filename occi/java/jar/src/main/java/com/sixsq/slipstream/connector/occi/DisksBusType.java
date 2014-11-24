package com.sixsq.slipstream.connector.occi;

import java.util.ArrayList;
import java.util.List;

public enum DisksBusType
{
  VIRTIO("virtio"), SCSI("scsi");

  private final String value;

  private DisksBusType(String value) {
    this.value = value;
  }

  public String getValue() {
    return this.value;
  }

  public static List<String> getValues() {
    List<String> types = new ArrayList<String>();

    for (DisksBusType type : values()) {
      types.add(type.getValue());
    }
    return types;
  }
}
