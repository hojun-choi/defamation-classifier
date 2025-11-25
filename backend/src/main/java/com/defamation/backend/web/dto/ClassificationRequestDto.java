package com.defamation.backend.web.dto;

import com.defamation.backend.domain.ClassificationRequest;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.*;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

@Getter @Setter
@AllArgsConstructor @NoArgsConstructor
@Builder
public class ClassificationRequestDto {

    private Long id;

    private String problemSituation;
    private Long modelId;

    private List<String> caseNames;

    private String sentenceType;
    private Long sentenceValue;
    private Integer sentenceSuspension;
    private String sentenceAdditionalOrder;
    private String sentenceReason;
    private String sentenceJudgment;

    private LocalDateTime createdAt;

    public static ClassificationRequestDto from(ClassificationRequest r, ObjectMapper om) {
        return ClassificationRequestDto.builder()
                .id(r.getId())
                .problemSituation(r.getProblemSituation())
                .modelId(r.getModelId())
                .caseNames(parseList(om, r.getCaseNames()))
                .sentenceType(r.getSentenceType())
                .sentenceValue(r.getSentenceValue())
                .sentenceSuspension(r.getSentenceSuspension())
                .sentenceAdditionalOrder(r.getSentenceAdditionalOrder())
                .sentenceReason(r.getSentenceReason())
                .sentenceJudgment(r.getSentenceJudgment())
                .createdAt(r.getCreatedAt())
                .build();
    }

    private static List<String> parseList(ObjectMapper om, String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return om.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return List.of(json);
        }
    }
}
