package com.defamation.backend.web.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PredictRequest {
    private String inputs;
    private Long modelId;
}
