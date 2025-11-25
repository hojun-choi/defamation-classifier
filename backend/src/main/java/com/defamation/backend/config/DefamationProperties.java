package com.defamation.backend.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.HashMap;
import java.util.Map;

@Getter
@Setter
@ConfigurationProperties(prefix = "defamation")
public class DefamationProperties {

    /**
     * modelId -> FastAPI URL (/predict)
     * application.yml:
     * defamation.model-endpoints.1 = "https://xxx.ngrok-free.dev/predict"
     */
    private Map<Long, String> modelEndpoints = new HashMap<>();
}
